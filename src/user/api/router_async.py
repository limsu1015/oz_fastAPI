from fastapi import APIRouter, Path, Body, status, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database.connection_async import get_async_session
from user.service.authentication import check_password, encode_access_token, authenticate
from user.models import User
from user.schema.request import SignUpRequestBody
from user.schema.response import UserMeResponse, UserResponse, JWTResponse

router = APIRouter(prefix="/user", tags=["AsyncUser"])

# db = [
#     {
#         "username": "admin", # pw: 0123
#         "password": '$2b$12$ZAljusj1MiNMlr4Mw.RCO.w3QI.qfk1GELqXJTruxolY8G/W.55H.'
#     },
#     {
#         "username": "admin2", # pw: 1234
#         "password": '$2b$12$vG2aLMurNKbO8eF4qteWMeWh2/xCkbMzVzBVS8WM574O7Yzdf0t4S'
#     }
# ]

# 회원 가입 api
# 1) 사용자로부터 username, password
# 2) username, password 검증 (중복된 username 있는지)
# 3) DB에 저장(hashing)

# Path: 모든 요청에 대해서 쓰임
# Query: GET 요청에서 주로 쓰임
# Body: POST 요청에서 주로 쓰임

@router.post("",
             response_model=UserMeResponse,
             status_code=status.HTTP_201_CREATED)
async def sign_up_handler(
    body: SignUpRequestBody,
    session: AsyncSession = Depends(get_async_session),
): # 저장되기 전

    new_user = User.create(username=body.username, password=body.password)
    session.add(new_user)
    await session.commit()  # db 저장

    return UserMeResponse(
        id=new_user.id, username=new_user.username, password=new_user.password
    )


@router.post(
    "/login", response_model=JWTResponse,
    status_code=status.HTTP_200_OK)
async def login_handler(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
    session: AsyncSession = Depends(get_async_session),
):
    # 1) db에서 데이터 조회 -> I/O 발생
    result = await session.execute(
        select(User).filter(User.username == credentials.username)
    )
    # 2) FastAPI 서버 상에서
    user: User | None = result.scalar().first()

    # await -> I/O 대기가 발생하는 순간 = DB랑 실제로 통신하는 순간
    # .close() / .commit()

    # orm 데이터를 조회하는 건
    # 1) DB랑 통신
    # 2) sqlalchemt DB에서 가져온 데이터를 user 객체로 변환


    if user:
        if check_password(
            plain_text=credentials.password,
            hashed_password=user.password,
        ):
            return JSONResponse(
                aaccess_token=encode_access_token(user_id=user.id),
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

# 내 정보 조회
@router.get("/me")
async def ge_me_handler(
    user_id: int = Depends(authenticate),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(User).filter(User.username == username))
    user: User | None = result.scalar().first()


    if user:
        return UserMeResponse(
            id=user.id, username=user.username, password=user.password
        )


    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )




# 사용자 조회 API(GET 127.0.0.1/users/{username}
# 1) 전달 받은 username에 해당하는 사용자를 조회
# 2) 조회된 사용자를 반환
@router.patch(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK)
async def update_user_handler(
    user_id: int = Depends(authenticate),
    new_password: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(User).filter(User.username == username))
    user: User | None = result.scalar().first()
    if user:
        user.update_password(password=new_password)
        session.add(user)
        session.commit()
        return UserMeResponse(
            id=user.id, username=user.username, password=user.password
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )



@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_user_handler(
    user_id: int = Depends(authenticate),
    session: AsyncSession = Depends(get_async_session),
):

    result = await session.execute(select(User).filter(User.username == username))
    user: User | None = result.scalar().first()
    if user:
        await session.delete(user)
        await session.commit()
        return
    # await  session.execute((delete(User).where(User.username == username)))
    # await session.commit()
    # return
    # raise HTTPException(
    #     status_code=status.HTTP_404_NOT_FOUND,
    #     detail="User not found"
    # )






# 다른사람 정보를 조회하는 경우
@router.get(
    "/{username}",
        response_model=UserResponse,
        status_code=status.HTTP_200_OK
)
async def get_user_handler(
        _: str = Depends(authenticate),
        username: str = Path(..., max_length=10),
        session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(User).filter(User.username == username))
    user: User | None = result.scalar().first()
    if user:
        return UserResponse(username=user.username)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )




