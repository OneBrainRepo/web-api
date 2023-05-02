from fastapi import Query, Request, APIRouter, Depends
from webapi.users.users import signupService
from webapi.auth.auth_dto import SignUpPayload
from webapi.auth.jwt import JWTGuard

router = APIRouter()
#Define Demo related routes here
"""
Firstly we define demo path here
Then we define normal login path here as well
Later on we will change the path which this router is prefixed as

"""


@router.get("/test")
def getDemoTest()-> dict:
    return {"message": "Hello World"}

@router.get("/protected-test")
async def protected_test(current_user: dict[str,str] = Depends(JWTGuard)):
    return {"message": "Protected Hello World"} 

@router.post("/signup")
async def users_signup(payload: SignUpPayload):
    return await signupService(payload)
    