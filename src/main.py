from datetime import datetime

from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, status, requests
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from feed import router as feed_router
from user.api import router as user_router
import httpx
import time
import requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="feed/posts"))
app.include_router(user_router.router)
app.include_router(feed_router.router)



@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc: RequestValidationError):

    return JSONResponse(
        content={"error": exc.errors()[0]["msg"]},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.exception_handler(ValueError)
def value_error_handler(request, exc):
    return JSONResponse(
        content={"error": str(exc)},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.exception_handler(httpx.HTTPStatusError)
def httpx_status_error_handler(request, exc):
    return JSONResponse(
        content={"error": str(exc)},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.get("/")
def health_check_handler():
    return {"ping": "pong"}



# @app.post("/images")
# def upload_image_handler(file: UploadFile):
#     return {
#         "filename": file.filename,
#         "content_type": file.content_type,
#         "file_size": file.size,
#     }

class NowResponse(BaseModel):
    now: datetime
@app.get("/now",
         response_model=NowResponse,
         description="## 설명\n현재 시간을 반환하는 api입니다.",
         status_code=status.HTTP_200_OK,
         )

async def now_handler():
    return NowResponse(now=datetime.now())



@app.get("/sync",)
def sync_handler():
    start_time = time.perf_counter()
    urls = [
        "https://jsonplaceholder.typicode.com/posts",
        "https://jsonplaceholder.typicode.com/posts",
        "https://jsonplaceholder.typicode.com/posts",
    ]
    responses = []
    for url in urls:
        responses.append(requests.get(url))
    end_time = time.perf_counter()
    return {
        "duration": end_time - start_time,

    }
@app.get("/async")
async def async_handler():
    start_time = time.perf_counter()

    urls = [
        "https://jsonplaceholder.typicode.com/posts",
        "https://jsonplaceholder.typicode.com/posts",
        "https://jsonplaceholder.typicode.com/posts"
    ]

    async with httpx.AsyncClient() as client:
        tasks = []
        for url in urls:
            tasks.append(client.get(url))
        import asyncio
        await asyncio.gather(*tasks)

    end_time = time.perf_counter()
    return {
        "duration": end_time - start_time,

    }














# 서버에서 I/O 대기가 발생하는 경우
# 외부 API 호출 (chatGPT, 크롤링, 소셜 로그인, ...)
# 2) 데이터베이스 통신 . commit
# 3) 파일 다룰 때
# 4) 웹 소켓 (채팅, 푸시 알람, ...)

# 정리
#FastAPI는 기본적으로 비동기 프로그래밍이 정용되어 있음
# 일반적으로는 비동기 프로그램 안에서 동기 프로그램 실행시키면 안됨
# 왜냐하면 동기 코드가 event loop를 blocking 시켜버림
# 그런데 gastapi는 동기 handler를 선언하더라도 비동기적으로 실행

# 조심ㅎ