import asyncio
import time


# 코루틴
# 비동기적 실행 할 수 있는 함수
# 중간에 코드 실행을 멈출 수 있음 -> 대기 발 생 -> 다르 작업

# async def doing_something():
#     print("잠깐만")
#     print("(다른 일 하는 중...)")
#

def sync_function():
    print("동기 함수")

async def async_function1():
    print("비동기 함수1")
    print("sleeping...")
    await asyncio.sleep(3)
    print("비동기 함수 1종료")

async def async_function2():
    print("비동기 함수2")
    print("sleeping...")
    await asyncio.sleep(3)
    print("비동기 함수 2종료")

async def main():
    start_time = time.time()
    coro1 = async_function1()
    coro2 = async_function2()
    await asyncio.gather(coro1, coro2)
    end_time = time.time()
    print(end_time-start_time)

asyncio.run(main())