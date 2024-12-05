from http import HTTPStatus

from fastapi import APIRouter, Path, Body, status, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from pydantic import BaseModel

from user.request import SignUpRequestBody, UserPasswordRequestBody
from user.response import UserResponse, UserMeResponse

router = APIRouter(prefix="/user", tags=["user"])

db = [
    {
        "username": "admin",
        "password": "0123",
    },
    {
        "username": "admin2",
        "password": "1234",
    }
]

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
def sign_up_handler(body: SignUpRequestBody):
    new_user = {
        "username": body.username,
        "password": body.password,
    }
    db.append(new_user)
    return UserUpdateRequestBody(
        username=new_user["username"],
        password=new_user["password"],
    )

# 내 정보 조회
@router.get("/me")
def ge_me_handler(
        credentials: HTTPBasicCredentials = Depends(HTTPBasic())
):
    for user in db:
        if user["username"] == credentials.username:
            if user["password"] == credentials.password:
                return UserMeResponse(
                    username=user["username"], password=user["password"]
                )
            else:
                # 비밀번호 틀린경우
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


    return

# 사용자 조회 API(GET 127.0.0.1/users/{username}
# 1) 전달 받은 username에 해당하는 사용자를 조회
# 2) 조회된 사용자를 반환
@router.patch(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK)
def update_user_handler(
        credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
        # body: UserPasswordRequestBody=Body(...),
        new_password: str = Body(..., embed=True),
):
    for user in db:
        if user["username"] == credentials.username:

            if user["password"] != credentials.password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password",
                )

            user["password"] = new_password
            return UserMeResponse(
                username=user["username"],
                password=user["password"],
            )


    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

@router.get(
        "/{username}",
            response_model=UserResponse,
            status_code=status.HTTP_200_OK
)
def get_user_handler(
        username: str = Path(..., max_length=10)
):
    for user in db:
        if user["username"] == username:
            return UserResponse(username=user["username"])

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

class UserUpdateRequestBody(BaseModel):
    password: str



@router.delete("/{username}",status_code=status.HTTP_204_NO_CONTENT)
def delete_user_handler(
        username: str = Path(..., max_length=10)
):
    for user in db:
        if user["username"] == username:
            db.remove(user)
            return



    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="User not found"
    )
