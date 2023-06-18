from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBaseDTO(BaseModel):
    id : int
    username: str
    email: str | None = None
    disabled: bool | None = None

class UserInDB(UserBaseDTO):
    hashed_password: str

class SignUpPayload(BaseModel):
    username: str
    password: str

class DemoSignupPayload(BaseModel):
    userid: str
    hashed_password: str