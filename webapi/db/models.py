from typing import Dict, Union, Optional
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, TIMESTAMP, Column, func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

