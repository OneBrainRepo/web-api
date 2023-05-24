from typing import Dict, Union, Optional
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, TIMESTAMP, Column, func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
import uuid


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: Optional[str] = Field(default=str(uuid.uuid4()))
    username: str
    hashed_password: str
    email: str | None = None
    disabled: bool | None = None

class Demo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userid: str
    hashed_password: str

class ConnectionRequests(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    connection_id : str
    connection_title : Optional[str]
    state: int
