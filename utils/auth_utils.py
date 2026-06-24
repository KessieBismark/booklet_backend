
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from strawberry.exceptions import GraphQLError
from config.dbconfig import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


async def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    def _create_token():
        to_encode = data.copy()
        to_encode["type"] = "access"
        expire = (
            datetime.now(timezone.utc) + expires_delta
            if expires_delta
            else datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return await asyncio.to_thread(_create_token)


async def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    #Create a long-lived refresh token (signed with type='refresh').
    def _create_token():
        to_encode = data.copy()
        to_encode["type"] = "refresh"
        expire = (
            datetime.now(timezone.utc) + expires_delta
            if expires_delta
            else datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return await asyncio.to_thread(_create_token)


async def verify_refresh_token(token: str) -> dict:
    #Decode and validate a refresh token.  Raises GraphQLError on failure.
    def _decode():
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                raise GraphQLError(
                    "Invalid token type",
                    extensions={"code": "SESSION_EXPIRED"}
                )
            return payload
        except JWTError:
            raise GraphQLError(
                "Session expired — please log in again",
                extensions={"code": "SESSION_EXPIRED"}
            )

    return await asyncio.to_thread(_decode)


async def decode_token(token: str) -> Optional[dict]:
    def _decode_token():
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return None

    return await asyncio.to_thread(_decode_token)

    