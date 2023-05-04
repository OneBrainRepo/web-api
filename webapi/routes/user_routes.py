from fastapi import Query, Request, APIRouter, Depends
from webapi.users.users import sign_in, sign_up, demo_login_only
from webapi.auth.auth_dto import SignUpPayload, DemoSignupPayload
from webapi.users.users_dto import UserSignIn
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
    print(current_user)
    print(f"Current user id : {current_user.id}")
    return {"message": "Protected Hello World"} 

@router.post("/signin")
async def users_signin(payload: SignUpPayload):
    return sign_in(payload)

@router.post("/signup")
async def user_signup(payload:UserSignIn):
    sign_up(payload=payload)
    return {"message": "Registration has been succesful"} 
    