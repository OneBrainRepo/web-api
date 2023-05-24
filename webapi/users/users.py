from webapi.auth.auth_dto import SignUpPayload, TokenData, DemoSignupPayload
from webapi.auth.jwt import authenticate_user, create_jwt_token, return_decoded_token, get_user, get_password_hash, demo_jwt_token
from webapi.db.CRUD import find_first, create
from webapi.db.models import Users, Demo, ConnectionRequests
from webapi.users.users_dto import UserSignIn, ConnectionRequestBase
from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt

def find_user_by_email(email:str):
    return find_first(Users,filter_by={"email":email})

def sign_in(payload:SignUpPayload):
    # Check current user in DB
    # Will handle under create_jwt_token
    # Write to a table about X-CSFR token and keep track of it with sessions
    access_token = create_jwt_token(payload=payload)
    return {"access_token": access_token, "token_type": "bearer"}

def sign_up(payload:UserSignIn):
    # Check if required some prequsities
    newUser = Users(username=payload.username,hashed_password=get_password_hash(payload.hashed_password),email=payload.email)
    create(Users,newUser)

def save_connection_request(payload:ConnectionRequestBase):
    # Save connection request to db if it matches with email in the user table
    foundUser = find_user_by_email(payload.connection_id) # Connection ID is email
    if not foundUser:
        raise HTTPException(404,"User is not found")
    newConnection = ConnectionRequests(connection_id=payload.connection_id,connection_title=payload.connection_title,state=payload.state,user_id=foundUser.id)
    create(ConnectionRequests,newConnection)


def get_current_user(token:str):
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = return_decoded_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

# DO NOT DEFINE ANY GUARDS HERE
# ONLY SERVICES
# GUARDS ARE DEFINED EITHER AS MIDDLEWARE OR IN THE AUTH MODULE
# ALSO DO NOT MAKE IT DEPENDENT HERE ONLY IN THE ROUTES

# DEMO ONLY LOGIN
# DO NOT USE IT IN PRODUCTION
def demo_login_only(payload:DemoSignupPayload):
    """
    DEMO ACCESS ONLY
    Checks for demo user in database and if yes returns token
    No actual check for X-CSFR token will be implemented
    Needs to be erased after demo
    Demo Signup is only done via manually
    """
    return {"access_token": demo_jwt_token(payload=payload), "token_type": "bearer"}

def demo_user_crete(payload:DemoSignupPayload):
    """
    Demo access only
    It wouldnt be served on the any routes, just internal access to create users
    Needs to be erased after the demo
    """
    newDemouser = Demo(userid=payload.userid,hashed_password=get_password_hash(payload.hashed_password))
    create(Demo,newDemouser)