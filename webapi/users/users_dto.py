from pydantic import BaseModel
from typing import Optional

class UserSignIn(BaseModel):
    username: str
    hashed_password: str
    email: str | None = None


class UserPublic(BaseModel):
    email: str
    id: int
    username: str

class ConnectionRequestBase(BaseModel):
    connection_id: str
    connection_title : Optional[str] = None
    state: str
    error: Optional[str] = None

class SessionVerifyPayload(BaseModel):
    session_id: str