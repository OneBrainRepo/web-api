"""
Only Demo User related routes
No other specific things
"""

from fastapi import Query, Request, APIRouter, Depends
from webapi.auth.jwt import JWTGuard
from webapi.users.users import demo_login_only
from webapi.auth.auth_dto import DemoSignupPayload

router = APIRouter()

@router.get("/test")
def getDemoTest()-> dict:
    return {"message": "Hello World"}

@router.get("/protected-test")
async def protected_test(current_user: dict[str,str] = Depends(JWTGuard)):
    return {"message": "Protected Hello World"} 

@router.post("/signin")
async def demo_signin(payload: DemoSignupPayload):
    return await demo_login_only(payload)