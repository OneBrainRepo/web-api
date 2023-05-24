from webapi.mongo.CRUD import *
from webapi.conversation.conversation_dto import ChatHistoryByID, ChatHistoryAppend, ChatUpdateTitle, ChatUpdateMessage, ChatHistoryCreate
from webapi.users.users_dto import UserPublic
from webapi.mongo.models import Author, ChatHistory
from fastapi import HTTPException
from typing import Any
from uuid import uuid4

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
    found_author = read("Author", author_id=userid)
    if found_author is None:
        raise create_exception_404
    return found_author

def findOrCreateUser(userid:int,name:str):
    found_author = read("Author", author_id=userid)
    if found_author is not None:
        return found_author
    found_author = create("Author", author_id=userid,name=name)
    return found_author

def covert_to_public_user_format(user_id):
    return UserPublic(
        email=user_id.email,
        id=user_id.id,
        username=user_id.username
    )

def get_last_conversation(userid:int) -> (dict[str, str] | dict[str, Any]) :
    """
    Parse user id into the field and return the last messages 
    No datetime just last message
    Id value should be parsed on the routes via jwt claims
    """
    # FIND USER ID FIRST
    foundUser = findUser(userid=userid)
    last_question, last_answer = read_last_conversation("ChatHistory", foundUser)
    print(f"Last question : {last_question}\nLast answer : {last_answer}")
    if last_question is None:
        return {"last_question":"none","last_answer":"none"}
    return {"last_question":last_question,"last_answer":last_answer}

def add_conversation(payload:ChatHistoryCreate,userid:dict[str,str]):
    author = findOrCreateUser(userid=userid.id,name=userid.username)
    try:
        if author is None:
            author = create("Author", name=userid.username, author_id=userid.id)

        NewChat = create(
            "ChatHistory", 
            title=payload.title, 
            author=author, 
            UserQuestions=[payload.UserQuestions], 
            MachineAnswers=[payload.MachineAnswers]
        )
        public_user = covert_to_public_user_format(user_id=userid)
        return {"user":public_user,"question":payload.UserQuestions,"answer":payload.MachineAnswers,"chatHistory":NewChat.to_mongo().to_dict()}
    except Exception as e:
        print(f"Error type: {type(e)}")
        print(f"Error on /create endpoint\n{e}")
        raise create_exception_500

# def add_test(payload:ChatHistoryCreate,userid:dict[str,str]):
#     try:
#         # Later on this needs to be called inside append if there is no conversation avaliable
#         # author = create("Author", name=userid.username, author_id=userid.id)
#         author = findUser(userid=userid.id)
#         print(f"Author : {author.name}")
#         NewChat = create("ChatHistory", title=payload.title, author=author, UserQuestions=[payload.UserQuestions], MachineAnswers=[payload.MachineAnswers])
#         return author
#     except Exception as e:
#         print(f"Error on /test endpoint\n{e}")
#         raise create_exception_500

def append_conversation_latest(payload:ChatHistoryAppend,userid:int):
    author = findUser(userid=userid)
    chat_histories = read_by_filter_and_order("ChatHistory", order="-createdAt", author=author)
    print(f"chat_histories : {chat_histories}")
    if not chat_histories:
        return create_exception_404
    found_chat_history =  chat_histories[0]
    try:
        updated_chat_history  = update_one(
        "ChatHistory",
        found_chat_history,
        push__UserQuestions=payload.UserQuestions,
        push__MachineAnswers=payload.MachineAnswers
        ) 
        # return the updated data
        if updated_chat_history is None:
            raise create_exception_500
        return {
            "status": "success",
            "message": "Conversation appended successfully.",
            "data": updated_chat_history.to_mongo().to_dict()
            }
    except Exception as e:
        print(f"Error on /append_latest endpoint\n{e}")
        raise create_exception_500

def append_conversation(payload:ChatHistoryAppend,userid:int):
    found_chat = read_by_id("ChatHistory",payload.id)
    if found_chat is None:
        return create_exception_401
    if found_chat.author.author_id != userid:
        return create_exception_401
    try:
        updated_chat_history  = update_one(
        "ChatHistory",
        found_chat,
        push__UserQuestions=payload.UserQuestions,
        push__MachineAnswers=payload.MachineAnswers
        ) 
        # return the updated data
        if updated_chat_history is None:
            raise create_exception_500
        return {
            "status": "success",
            "message": "Conversation appended successfully.",
            "data": updated_chat_history.to_mongo().to_dict()
            }
    except Exception as e:
        print(f"Error on /append endpoint\n{e}")
        raise create_exception_500


def get_all_conversation(userid:int):
    author = findUser(userid=userid)
    print(f"Author found : {author}")
    found_chats = read_many("ChatHistory", author=author)
    if found_chats is None:
        raise create_exception_404
    return found_chats


def get_all_titles(userid:int):
    author = findUser(userid=userid)
    print(f"Author found : {author}")
    found_chats = read_all_title("ChatHistory", author=author)
    if found_chats is None:
        raise create_exception_404
    return found_chats

def get_specific_coversation(userid:int,chatid:str):
    # Check if user is owner
    try:
        # print(f"Parsed datas : {userid} and {chatid}")
        foundChat = read_by_id("ChatHistory",chatid)
        # print(foundChat)
        # print(f"User ID : {userid}\nDocument Owner ID : {foundChat.author.author_id}\nIF EQ : {userid == foundChat.author.author_id}")
        if foundChat.author.author_id == userid:
            # Parse the foundChat
            return foundChat.to_mongo().to_dict()
        return create_exception_401
    except Exception as e:
        print(f"Exception : {e}")
        raise create_exception_401

def get_specific_coversation_object(userid:int,chatid:str):
    # Check if user is owner
    try:
        # print(f"Parsed datas : {userid} and {chatid}")
        foundChat = read_by_id("ChatHistory",chatid)
        # print(foundChat)
        # print(f"User ID : {userid}\nDocument Owner ID : {foundChat.author.author_id}\nIF EQ : {userid == foundChat.author.author_id}")
        if foundChat.author.author_id == userid:
            # Parse the foundChat
            return foundChat
        return create_exception_401
    except Exception as e:
        print(f"Exception : {e}")
        raise create_exception_401

def change_conversation_title(payload:ChatUpdateTitle,userid:int):
    try:
        # found_chat = get_specific_coversation(userid=userid,chatid=payload.id)
        found_chat = read_by_id("ChatHistory",payload.id)
        if found_chat is None:
            return create_exception_401
        if found_chat.author.author_id != userid:
            return create_exception_401

        updated_chat_history  = update_one(
        "ChatHistory",
        found_chat,
        set__title=payload.title,
        ) 
        # return the updated data
        if updated_chat_history is None:
            raise create_exception_500
        return {
            "status": "success",
            "message": "Title has been changed successfully.",
            "data": updated_chat_history.to_mongo().to_dict()
            }
    except Exception as e:
        print(f"Error on /edit_title endpoint\n{e}")
        raise create_exception_500

def change_user_message(payload:ChatUpdateMessage,userid:int):
    try:
        found_chat = get_specific_coversation(userid=userid,chatid=payload.id)
        # CALL THE API ENDPOINT TO GENERATE ANSWER AGAIN
        """
        LATER ON IT NEEDS TO BE QUEUED VIA REDIS OR SOMETHING TO MAKE A CHANGE THEN UPDATE THE MACHINE ANSWER
        IN FIRST STAGES CALL API AGAIN AND WAIT FOR THE ANSWER
        KEEPING IT TILL MVP
        """
        # CALL THE API ENDPOINT TO GENERATE ANSWER AGAIN
        updated_chat_history  = update_one(
        "ChatHistory",
        found_chat,
        set__UserQuestions=payload.Chat_UserQuestion_single,
        ) 
        # return the updated data
        if updated_chat_history is None:
            raise create_exception_500
        return {
            "status": "success",
            "message": "Message has been changed successfully.",
            "data": updated_chat_history.to_mongo().to_dict()
            }
    except Exception as e:
        print(f"Error on /edit_message endpoint\n{e}")
        raise create_exception_500

def delete_user_message(id:str,userid:int):
    try:
        found_chat = get_specific_coversation_object(userid=userid,chatid=id)
        delete_one(found_chat)
        return True
    except Exception as e:
        print(f"Error on /edit_message endpoint\n{e}")
        raise create_exception_500