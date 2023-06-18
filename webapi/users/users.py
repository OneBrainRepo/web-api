from webapi.auth.auth_dto import SignUpPayload, TokenData, DemoSignupPayload
from webapi.auth.jwt import authenticate_user, create_jwt_token, return_decoded_token, get_user, get_password_hash, demo_jwt_token
from webapi.db.CRUD import find_first, create, update
from webapi.db.models import Users, Demo, ConnectionRequests, MessageCounter, ConnectionRequests
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
    createdUser = create(Users,newUser)
    counterdemo = MessageCounter(user_id=createdUser.id)
    create(MessageCounter,counterdemo)

def save_connection_request(payload:ConnectionRequestBase):
    # Save connection request to db if it matches with email in the user table
    useremail = payload.connection_id.split('_')[-1]
    print(f"User : {useremail}")
    foundUser = find_user_by_email(useremail) # Connection ID is email
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

def check_total_message_left(userid:int):
    try:
        foundUsersMessageCounter = find_first(MessageCounter,filter_by={"user_id":userid})
        print(f"Found message table : {foundUsersMessageCounter}")
        if foundUsersMessageCounter == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not Found",
            )
    # return UserInDB(username='example',email='example@example.com',full_name='exampleDOMAIN',disabled=False,hashed_password='hashedExamplePassword')
        return foundUsersMessageCounter
    except Exception as e:
        print(f"Exception occured on check total message\nException : {e}")
        return e


def allow_block_limit_for_message(userid:int):
    """Returns True if user has reached the message limit"""
    try:
        foundUsersMessageCounter = find_first(MessageCounter,filter_by={"user_id":userid})
        if(foundUsersMessageCounter.current_amount >= foundUsersMessageCounter.max_message):
            return True
        return False
    except Exception as e:
        print(f"Exception occured on check total message\nException : {e}")
        return e

def increment_message_usage(userid:int,incrementation:int=1):
    try:
        foundUsersMessageCounter = check_total_message_left(userid=userid)
        print(f"Found Message qoute : {foundUsersMessageCounter}")
        update(MessageCounter, foundUsersMessageCounter.id, {"current_amount": foundUsersMessageCounter.current_amount+incrementation})
        return True
    except Exception as e:
        print(f"Exception at Increment message usage.\n{e}")
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error on Message Counter",
            )

def find_connection_id(userid:int):
    foundConnectionId = find_first(ConnectionRequests,filter_by={"user_id":userid})
    print(f"DEBUGGING ONLY FOUND USER : {foundConnectionId}")
    if foundConnectionId:
        return foundConnectionId
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User does not have any connection ID. Please connect with OAuth application to provide this information")
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