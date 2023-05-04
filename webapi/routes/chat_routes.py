from fastapi import Query, Request, APIRouter, Depends
from webapi.conversation.conversations import *
from webapi.conversation.conversation_dto import *
from webapi.auth.jwt import JWTGuard

router = APIRouter()

@router.get("/protected-test")
def protected_test(current_user: dict[str,str] = Depends(JWTGuard)):
    return {"message": "Protected Hello World"} 

@router.get("/last")
def last_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_last_conversation(current_user.get("id"))

@router.get("/all")
def all_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_all_conversation(current_user.get("id"))

@router.get("/specific")
def specific_conversation(chatid : int ,current_user: dict[str,str] = Depends(JWTGuard)):
    return get_specific_coversation(userid=current_user.get("id"),chatid=chatid)

@router.post("/append")
def append_to_conversation(payload:ChatHistoryAppend,current_user: dict[str,str] = Depends(JWTGuard)):
    return append_conversation(payload=payload,userid=current_user.get("id"))

