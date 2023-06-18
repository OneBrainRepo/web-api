"""
Both middleware and handlers will be here
In the beginning we will be using Firebase Auth
Later on We need to create our own anyway

ALSO ADD X-CSRF TOKEN IN THE JWT CLAIMS AS WELL AND SAVE IT IN THE DATABASE UNDER SESSIONS
THERE WILL BE A DOCUMENT DB WHICH STORES THE SESSIONS
CREATE A ENTRY OVER THERE WITH USERNAME OR ID AND HOLD XCSFR TOKEN WITH SESSION ID
"""
from webapi.auth.auth_dto import UserInDB, SignUpPayload, DemoSignupPayload, UserBaseDTO
from webapi.db.CRUD import find_first
from webapi.db.models import Users, Demo
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
# import jwt
import uuid
import os

SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/signup")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    foundUsers = find_first(Users,filter_by={"username":username})
    if foundUsers == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not Found",
            headers={'WWW-Authenticate': 'Bearer realm="auth_required"'},
        )
    # return UserInDB(username='example',email='example@example.com',full_name='exampleDOMAIN',disabled=False,hashed_password='hashedExamplePassword')
    return foundUsers

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return UserBaseDTO(
        id=user.id,
        uuid=user.uuid,
        username=user.username,
        email=user.email,
        disabled=user.disabled
    )

def create_jwt_token(payload: SignUpPayload, expires_delta: timedelta = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    x_csfr = str(uuid.uuid4())
    user = authenticate_user(username=payload.username,password=payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not Found",
            headers={'WWW-Authenticate': 'Bearer realm="auth_required"'},
        )
    print(f"User data : {user}")
    # ONE BELOW SENDS EVERYTHING IN THE PAYLOAD IT IS USED FOR TESTING
    # to_encode = {"exp": expire, "x-csfr": x_csfr, **payload.dict()}
    to_encode = {"exp": expire, "x-csfr": x_csfr,"id":user.id, "user_data": user.dict()}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def return_decoded_token(jwt_token : str) -> dict:
    # Check also for x_csft token later on here to protect against csfr attack
    # x_csfr needs to be stored somewhere preferrably nosql db
    payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
    x_csfr: str = payload.get("x-csfr")
    if x_csfr is None:
        return None
    return payload

def JWTGuard(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        x_csfr: str = payload.get("x-csfr")
        if x_csfr is None:
            raise credentials_exception
        username: str = payload.get("user_data")["username"]
        if username is None:
            raise credentials_exception
        # find User and return
        foundUser = get_user(username=username)
        if foundUser is None:
            raise credentials_exception
        return foundUser
    except:
        raise credentials_exception
    

# All of the code below is well complicated and not necessary

# DEMO ONLY JWT CREATOR
# ERASE IT AFTER DEMO

def demo_jwt_token(payload:DemoSignupPayload, expires_delta: timedelta = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    x_csfr = str(uuid.uuid4())
    # FIND USER AND ADD ID TO CLAIMS
    foundDemoUser = find_first(Demo,filter_by={"userid":payload.userid})
    if foundDemoUser is None:
        raise credentials_exception
    to_encode = {"exp": expire, "x-csfr": x_csfr, "userid":foundDemoUser.userid,"id":id}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# async def get_current_user(token: str):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     # CREATE A FUNCTION TO SEARCH ON DATABASE WHERE USERNAME MATCHES ON DATABASE PART
#     # RETURN A PART THAT COULD BE USED IN THE CLAIMS
#     user = True #get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user

# # USED AS GUARD, DO NOT TOUCH IT
# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user