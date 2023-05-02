from webapi.auth.auth_dto import SignUpPayload, TokenData
from webapi.auth.jwt import authenticate_user, create_jwt_token, return_decoded_token, get_user, oauth2_scheme
from webapi.db.CRUD import find_first
from webapi.db.models import Users
from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt

def signupService(payload:SignUpPayload):
    # Check current user in DB
    user = authenticate_user(username=payload.username,password=payload.password)
    # Write to a table about X-CSFR token and keep track of it with sessions
    return {"access_token": create_jwt_token(payload=payload), "token_type": "bearer"}

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