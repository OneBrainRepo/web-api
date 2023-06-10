from fastapi import Query, Request, APIRouter, Depends
from fastapi.responses import RedirectResponse
from webapi.users.users import sign_in, sign_up, demo_login_only, save_connection_request, check_total_message_left, increment_message_usage
from webapi.auth.auth_dto import SignUpPayload, DemoSignupPayload
from webapi.users.users_dto import UserSignIn, ConnectionRequestBase
from webapi.auth.jwt import JWTGuard
import os

router = APIRouter()
#Define Demo related routes here
"""
Firstly we define demo path here
Then we define normal login path here as well
Later on we will change the path which this router is prefixed as

"""

FRONT_END_URL = os.getenv("FRONT_END_URL","localhost:3000") 


@router.get("/test")
def getDemoTest()-> dict:
    return {"message": "Hello World"}

@router.get("/protected-test")
async def protected_test(current_user: dict[str,str] = Depends(JWTGuard)):
    print(f"Current user id : {current_user.id}")
    return {"message": "Protected Hello World"} 

@router.post("/signin")
async def users_signin(payload: SignUpPayload):
    return sign_in(payload)

@router.post("/signup")
async def user_signup(payload:UserSignIn):
    sign_up(payload=payload)
    return {"message": "Registration has been succesful"} 

@router.get("/messagecount")
def getTotalMessageleft(current_user: dict[str,str] = Depends(JWTGuard)):
    print(f"Current user id : {current_user.id}")
    return check_total_message_left(userid=current_user.id)

@router.get("/messagecountincr")
def getTotalMessageleft(current_user: dict[str,str] = Depends(JWTGuard)):
    print(f"Current user id : {current_user.id}")
    return increment_message_usage(userid=current_user.id,incrementation=5)

#Onlizer authenticate
@router.get("/connect")
async def user_redirect(payload:ConnectionRequestBase):
    # connection_id:str,state:int,connection_title:str, error:str
    # Those information is not correct yet, confirm with Onlizer API to ensure the correction of parameters
    save_connection_request(payload=payload)
    return RedirectResponse(f"{FRONT_END_URL}/chat?connection_id={payload.connection_id}&state={payload.state}")