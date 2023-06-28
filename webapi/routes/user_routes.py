from fastapi import Query, Request, APIRouter, Depends
from fastapi.responses import RedirectResponse
from webapi.users.users import sign_in, sign_up, demo_login_only, save_connection_request, check_total_message_left, increment_message_usage, find_connection_id, create_or_update_session, check_session_validity
from webapi.auth.auth_dto import SignUpPayload, DemoSignupPayload
from webapi.users.users_dto import UserSignIn, ConnectionRequestBase, SessionVerifyPayload
from webapi.auth.jwt import JWTGuard
from typing import Optional
import os

router = APIRouter()
#Define Demo related routes here
"""
Firstly we define demo path here
Then we define normal login path here as well
Later on we will change the path which this router is prefixed as

"""

FRONT_END_URL = os.getenv("FRONT_END_URL","http://localhost:3000") 


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

# Need to adjust /connect endpoint

#Onlizer authenticate
@router.get("/connect")
def user_redirect(connection_id: str,state: str,connection_title : Optional[str] = None,error: Optional[str] = None):
    # Check for Error
    if error:
        return RedirectResponse(f"{FRONT_END_URL}/signin")
    returnedDbEntry = create_or_update_session(connection_id=connection_id,state=state,connection_title=connection_title)
    if not returnedDbEntry:
        return RedirectResponse(f"{FRONT_END_URL}/signin")
    redirect_url = f"{FRONT_END_URL}/chat?sessionid={returnedDbEntry.session_id}"
    print(f"Redirect URL : {redirect_url}")
    print(f"[DELETEINPROD] DB ENTRY : {returnedDbEntry}")
    return RedirectResponse(redirect_url)

#Onlizer Check
# ERASE IN PRODUCTION
@router.get("/check")
def onlizer_check(connection_id: str,state: int,connection_title : Optional[str] = None,error: Optional[str] = None,current_user: dict[str,str] = Depends(JWTGuard)):
    foundUser = find_connection_id(userid=current_user.id)
    return foundUser

#Session Verifier
@router.post("/session")
def onlizer_check(payload : SessionVerifyPayload,current_user: dict[str,str] = Depends(JWTGuard)):
    # CHECK SESSION ID AND COMPARE WITH CURRENT USER'S EMAIL, IF TRUE RETURN 200 ELSE 404
    print(f"Session id for /session endpoint : {payload.session_id}")
    return check_session_validity(payload,current_user)