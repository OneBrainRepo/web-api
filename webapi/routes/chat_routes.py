from fastapi import Query, Request, APIRouter, Depends, status
from webapi.conversation.conversations import *
from webapi.conversation.conversation_dto import *
from webapi.auth.jwt import JWTGuard

router = APIRouter()

@router.get("/protected-test")
def protected_test(current_user: dict[str,str] = Depends(JWTGuard)):
    return {"message": "Protected Hello World"} 

# Tested Ok
@router.get("/last")
def last_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_last_conversation(current_user.id)

# Tested OK
@router.get("/all")
def all_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_all_conversation(current_user.id)

# Tested OK
@router.get("/specific")
def specific_conversation(chatid : str ,current_user: dict[str,str] = Depends(JWTGuard)):
    return get_specific_coversation(userid=current_user.id,chatid=chatid)

"""
Below needs to be Kafka initiated

Note : edit_message is currently not implemented yet
Ideally decided to run Kafka consumer operations in a seperate container therefore here are the new ways

append - Communicates with darwinapi to get the response, produce message called `write_to_db_append`
edit_title - Sends ok to user and edits in the front end, produce message called `write_to_db_edit_title`
edit_message - Sends message directly to darwin-api and waits for the response, produce message called `write_to_db_edit_message`

"""

@router.post("/append")
def append_to_conversation(payload:ChatHistoryAppend,current_user: dict[str,str] = Depends(JWTGuard)):
    return append_conversation(payload=payload,userid=current_user.id)

# Tested Ok will demolishit, everything about create or append should be at append endpoint
@router.post("/create")
def create_conversation(payload:ChatHistoryCreate,current_user: dict[str,str] = Depends(JWTGuard)):
    return add_conversation(payload=payload,userid=current_user)
# Tested OK | DO NOT INVOKE THIS ENDPOINT, PURPOSOLLY CREATED FOR DUPLICATE RECORDS HANDLING. WILL DEMOLISH SOON
@router.post("/test")
def create_conversation_test(payload:ChatHistoryCreate,current_user: dict[str,str] = Depends(JWTGuard)):
    return add_test(payload=payload,userid=current_user)

@router.post("/edit_title")
def change_title(payload:ChatUpdateTitle,current_user : dict[str,str] = Depends(JWTGuard)):
    return change_conversation_title(payload=payload,userid=current_user.id)

@router.post("/edit_message")
def change_message(payload:ChatUpdateMessage,current_user : dict[str,str] = Depends(JWTGuard)):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )
    # Return is disabled since this endpoint will be avaliable after demo
    # return change_user_message(payload=ChatUpdateMessage,userid=current_user.id)

