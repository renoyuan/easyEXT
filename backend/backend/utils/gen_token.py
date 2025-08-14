#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend gen_token
# CREATE_TIME: 2024/3/20 18:28
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
import jwt
from datetime import datetime, timedelta

# 密钥，用于加密和解密 JWT
SECRET_KEY = "mysecretkey"

# 生成 JWT Token
def create_jwt_token(user_info: dict) -> str:
    # 设置 JWT 的有效期为 一年
    expiration_time = datetime.utcnow() + timedelta(days=1*365)
    # 构造 JWT 的 payload
    payload = {
        "user_id": user_info["user_id"],
        "exp": expiration_time
    }
    # 使用密钥进行签名，生成 JWT Token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# 解析 JWT Token
def decode_jwt_token(token: str) -> dict:
    try:
        # 使用密钥解密 JWT Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # Token 已过期
        print("JWT Token 已过期")
        return None
    except jwt.InvalidTokenError:
        # Token 无效
        print("无效的 JWT Token")
        return None


if __name__ == "__main__":
    # 示例：创建 JWT Token
    user_id = 123
    user_info = {"user_id": user_id}
    jwt_token = create_jwt_token(user_info)
    print("JWT Token:", jwt_token)

    # 示例：解析 JWT Token
    decoded_payload = decode_jwt_token(jwt_token+"1")
    print("Decoded Payload:", decoded_payload)