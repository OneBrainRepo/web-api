from webapi.mongo.CRUD import *
from webapi.conversation.conversation_dto import ChatHistoryByID, ChatHistoryAppend
from fastapi import HTTPException
from typing import Any


"""
Define Exceptions
"""
create_exception_404=HTTPException(
        status_code=404,
        detail="User not found"
    )

create_exception_401=HTTPException(
    status_code=401,
    detail="User has no access to this document"
)

create_exception_500=HTTPException(
        status_code=500,
        detail="Internal Server Error"
    )

def findUser(userid:int):
    found_author = read("Author", id=userid)
    if found_author is None:
        raise create_exception_404
    return found_author


def get_last_conversation(userid:int) -> (dict[str, str] | dict[str, Any]) :
    """
    Parse user id into the field and return the last messages 
    No datetime just last message
    Id value should be parsed on the routes via jwt claims
    """
    last_question, last_answer = read_last_conversation("ChatHistory", userid)
    if last_question is None:
        return {"last_question":"none","last_answer":"none"}
    return {"last_question":last_question,"last_answer":last_answer}

def add_conversation(payload:ChatHistoryByID,userid:int):
    try:
        create("ChatHistory", title=ChatHistoryByID.title, author=userid, UserQuestions=[ChatHistoryByID.UserQuestions], MachineAnswers=[ChatHistoryByID.MachineAnswers])
        return {"user":userid,"question":ChatHistoryByID.UserQuestions,"answer":ChatHistoryByID.MachineAnswers}
    except:
        raise create_exception_500

def append_conversation(payload:ChatHistoryAppend,userid:int):
    chat_histories = read_by_filter_and_order("ChatHistory", order="-createdAt", author=userid)
    if not chat_histories:
        raise create_exception_404
    found_chat_history =  chat_histories[0]
    try:
        updated_chat_history  = update_one(
        "ChatHistory",
        found_chat_history,
        push__UserQuestions=ChatHistoryAppend.UserQuestions,
        push__MachineAnswers=ChatHistoryAppend.MachineAnswers
        ) 
        # return the updated data
        if updated_chat_history is None:
            raise create_exception_500
        return {
            "status": "success",
            "message": "Conversation appended successfully.",
            "data": updated_chat_history.to_mongo().to_dict()
            }
    except:
        raise create_exception_500

def get_all_conversation(userid:int):
    author = findUser(userid=userid)
    found_chats = read_many("ChatHistory", author=author)
    if found_chats is None:
        raise create_exception_404
    return found_chats

def get_specific_coversation(userid:int,chatid:int):
    # Check if user is owner
    try:
        foundChat = read_by_id("ChatHistory",chatid)
        if foundChat.author.id == userid:
            return foundChat
        raise create_exception_401
    except:
        raise create_exception_401
