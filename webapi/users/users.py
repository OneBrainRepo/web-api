from webapi.auth.auth_dto import SignUpPayload, TokenData, DemoSignupPayload
from webapi.auth.jwt import authenticate_user, create_jwt_token, return_decoded_token, get_user, get_password_hash, demo_jwt_token
from webapi.db.CRUD import find_first, create, update, upsert, update_if_exists, read
from webapi.db.models import Users, Demo, ConnectionRequests, MessageCounter, ConnectionRequests
from webapi.users.users_dto import UserSignIn, ConnectionRequestBase, SessionVerifyPayload
from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
from typing import Optional
import uuid

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

def find_session_by_user(user_id:int,state:str,email:str):
    foundConnectionId = find_first(ConnectionRequests,filter_by={"user_id":userid,"state":state})
    # Check email matching 
    if not foundConnectionId:
        useremail = foundConnectionId.connection_id.split('_')[-1]
        if useremail == email:
            return foundConnectionId.session_id
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User does not have any valid session")

def create_or_update_session(
    connection_id: str, 
    state: str, 
    connection_title: Optional[str] = None, 
    ) -> ConnectionRequests:
    try:
        # Check if it exist
        foundConnectionId = find_first(ConnectionRequests,filter_by={"connection_id":connection_id})
        if not foundConnectionId:
            newConnectionRequest = ConnectionRequests(connection_id=connection_id,connection_title=connection_title,state=state,session_id=uuid.uuid4())
            insertedRecord = create(ConnectionRequests,newConnectionRequest)
            return insertedRecord
        # If found
        newSessionId = uuid.uuid4()
        update(ConnectionRequests,foundConnectionId.id,{"state":state,"connection_title":connection_title,"session_id":newSessionId})
        # request = upsert(ConnectionRequests,connection_request)
        foundConnectionId.state = state
        foundConnectionId.connection_title = connection_title
        foundConnectionId.session_id = newSessionId
        return foundConnectionId
    except Exception as e:
        print(f"[LOGERR] Exception : {e}")
        return False

def check_session_validity(payload: SessionVerifyPayload, current_user: dict[str,str]) -> Optional[bool]:
    foundConnectionId = find_first(ConnectionRequests,filter_by={"session_id":payload.session_id})
    current_email = current_user.email
    user_id = current_user.id
    foundConnectionIdEmail = foundConnectionId.connection_id.split("__")[-1]
    print(f"Userid : {user_id}\nPayload : {payload.session_id}")
    # If foundConnection , then compare emails if not block access
    if not foundConnectionId:
        return {"isValid":False}
    # Check if user_id is null then update, otherwise it is ssession jacking
    print(f"Found connection : {foundConnectionId}")
    if foundConnectionId.user_id:
        # If user emails are matchinbg allow them
        if foundConnectionIdEmail == current_email:
            # If user is this person allow access
            update(ConnectionRequests,foundConnectionId.id,{"user_id":user_id})
            print(f"User Allowed")
            return {"isValid":True}
        # Session is owned by someone else and emails are not matching
        # Block the access
        print(f"User NOT Allowed")
        return {"isValid":False} 
    # If user id is empty update it
    update(ConnectionRequests,foundConnectionId.id,{"user_id":user_id})
    print(f"User Allowed")
    return {"isValid":True}
    # # Update if exists doesnt work well
    # session = update_if_exists(ConnectionRequests,{"session_id":payload.session_id},{"user_id":user_id})
    # if session is None:
    #     return {"isValid":False}
    # return {"isValid":True}



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