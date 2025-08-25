from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "idp_backend"
    admin_email: str = "renoyuan@foxmail.com"
    items_per_user: int = 50

    class Config:
        env_file = ".env"