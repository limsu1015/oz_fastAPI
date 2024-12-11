import os
from enum import StrEnum
from os import getenv

from pydantic_settings import BaseSettings


class SeverEnv(StrEnum):
    LOCAL = 'local'
    DEV = 'dev'
    PROD = 'prod'



class Settings(BaseSettings):
    database_url: str
    redis_host: str
    redis_port: int
    kakao_rest_api_key: str
    kakao_redirect_url: str


def get_settings(env: SeverEnv):
    match env:
        case SeverEnv.DEV:
            return Settings(_env_file="config/.env.dev")
        case SeverEnv.PROD:
            return Settings(_env_file="config/.env.prod")
        case _:
            return Settings(_env_file="config/.env.local")

ENV = os.getenv("ENV", SeverEnv.LOCAL)

settings = get_settings(ENV)