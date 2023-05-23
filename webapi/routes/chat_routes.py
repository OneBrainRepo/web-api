from fastapi import Query, Request, APIRouter, Depends, status
from fastapi.responses import Response
from webapi.conversation.conversations import *
from webapi.conversation.conversation_dto import *
from webapi.auth.jwt import JWTGuard

router = APIRouter()

@router.get("/protected-test")
def protected_test(current_user: dict[str,str] = Depends(JWTGuard)):
    print(f"UUID : {current_user.uuid}")
    return dict(current_user)

# Tested Ok
@router.get("/last")
def last_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_last_conversation(current_user.id)

# Tested OK
@router.get("/all")
def all_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_all_conversation(current_user.id)

# Tested OK
@router.get("/titles")
def all_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_all_titles(current_user.id)   

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
# Tested OK
# This endpoint will be used append to existing conversation
# Will NOT require document ID
# To append to the last message aka current message that user is writing
@router.post("/append_latest")
def append_to_conversation_latest(payload:ChatHistoryAppendLatest,current_user: dict[str,str] = Depends(JWTGuard)):
    return append_conversation_latest(payload=payload,userid=current_user.id)

# Tested OK
# This endpoint will be used to append to specific chat
# When user wants to continue on some old conversation we can use this
@router.post("/append")
def append_to_conversation(payload:ChatHistoryAppend,current_user: dict[str,str] = Depends(JWTGuard)):
    return append_conversation(payload=payload,userid=current_user.id)

# Tested Ok
# Used for opening a new chat window
# Creates also author if it doesnt exists
@router.post("/create")
def create_conversation(payload:ChatHistoryCreate,current_user: dict[str,str] = Depends(JWTGuard)):
    return add_conversation(payload=payload,userid=current_user)

# Tested OK
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

@router.get("/delete")
def delete_message(id:str,current_user : dict[str,str] = Depends(JWTGuard)):
    delete_user_message(id=id,userid=current_user.id)
    return Response(status_code=202)

# @router.get("/testdel")
# def testdel(params:str):
#     print(f"passed aprams : {params}")
#     return Response(status_code=201)