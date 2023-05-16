from pydantic import BaseModel

class UserSignIn(BaseModel):
    username: str
    hashed_password: str
    email: str | None = None


class UserPublic(BaseModel):
    email: str
    id: int
    username: str