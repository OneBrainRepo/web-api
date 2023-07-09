from webapi.mongo.CRUD import *
from webapi.conversation.conversation_dto import ChatHistoryByID, ChatHistoryAppend, ChatUpdateTitle, ChatUpdateMessage, ChatHistoryCreate, ChatHistoryAppendToEnd, Chat_MachineAnswer_single, ChatUpdateMessageByIndex, ChatUpdateMessageListByIndex
from webapi.users.users_dto import UserPublic
from webapi.mongo.models import Author, ChatHistory
from webapi.toolai.agent import agent_add_ai_messages,agent_add_human_messages,agent_awaitrun_with_messages,agent_awaitrun,generate_title_ai, duckduckgo_search_agent, tool_debug
from webapi.users.users import allow_block_limit_for_message, increment_message_usage, find_connection_id
from fastapi import HTTPException
from typing import Any
from uuid import uuid4
import re

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

def checkUserMessageAllowance(userid:int):
    allowance_message = allow_block_limit_for_message(userid=userid)
    DEMO_TRIAL_MESSAGE_END = """
    Thank you for trying the demo. Currently you have reached the message limit supported by the demo. It will be good to have your feedback as well
    Feel free to write to us directly for getting more information about current development stage or any other things.
    """
    if allowance_message:
        return {"message":DEMO_TRIAL_MESSAGE_END}

def findUserByEmail(email:str):
    found_author = read("Author", email=email)
    if found_author is None:
        raise create_exception_404
    return found_author

# def findOrCreateUser(userid:int,name:str):
#     found_author = read("Author", author_id=userid)
#     if found_author is not None:
#         return found_author
#     found_author = create("Author", author_id=userid,name=name)
#     return found_author

def findOrCreateUserByEmail(email:str,name:str):
    found_author = read("Author", email=email)
    if found_author is not None:
        return found_author
    found_author = create("Author", email=email,name=name)
    return found_author

def covert_to_public_user_format(user_id):
    return UserPublic(
        email=user_id.email,
        id=user_id.id,
        username=user_id.username
    )

def sanitize(input_string:str):
    return input_string
    # DISABLED FOR DEMO
    #return re.sub(r'[^A-Za-z0-9 _-]+', '', input_string)

def get_last_conversation(userid:dict[str,str]) -> (dict[str, str] | dict[str, Any]) :
    """
    Parse user id into the field and return the last messages 
    No datetime just last message
    Id value should be parsed on the routes via jwt claims
    """
    # FIND USER ID FIRST
    foundUser = findUserByEmail(email=userid.email)
    last_question, last_answer = read_last_conversation("ChatHistory", foundUser)
    print(f"Last question : {last_question}\nLast answer : {last_answer}")
    if last_question is None:
        return {"last_question":"none","last_answer":"none"}
    return {"last_question":last_question,"last_answer":last_answer}

def add_conversation(payload:ChatHistoryCreate,userid:dict[str,str]):
    author = findOrCreateUserByEmail(email=userid.email,name=userid.username)
    # author = findOrCreateUser(userid=userid.id,name=userid.username)
    try:
        if author is None:
            author = create("Author", name=userid.username, email=userid.email)

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

def append_conversation_latest(payload:ChatHistoryAppend,userid:dict[str,str]):
    author = findUserByEmail(email=userid.email)
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

def append_conversation(payload:ChatHistoryAppend,userid:dict[str,str]):
    found_chat = read_by_id("ChatHistory",payload.id)
    if found_chat is None:
        return create_exception_401
    if found_chat.author.email != userid.email:
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


def get_all_conversation(userid:dict[str,str]):
    author = findUserByEmail(email=userid.email)
    print(f"Author found : {author}")
    found_chats = read_many("ChatHistory", author=author)
    if found_chats is None:
        raise create_exception_404
    return found_chats


def get_all_titles(userid:dict[str,str]):
    author = findUserByEmail(email=userid.email)
    print(f"Author found : {author}")
    found_chats = read_all_title("ChatHistory", author=author)
    if found_chats is None:
        raise create_exception_404
    return found_chats

def get_specific_coversation(userid:dict[str,str],chatid:str):
    # Check if user is owner
    try:
        # print(f"Parsed datas : {userid} and {chatid}")
        foundChat = read_by_id("ChatHistory",chatid)
        # print(foundChat)
        # print(f"User ID : {userid}\nDocument Owner ID : {foundChat.author.author_id}\nIF EQ : {userid == foundChat.author.author_id}")
        if foundChat.author.email == userid.email:
            # Parse the foundChat
            return foundChat.to_mongo().to_dict()
        return create_exception_401
    except Exception as e:
        print(f"Exception : {e}")
        raise create_exception_401

def get_specific_coversation_object(userid:dict[str,str],chatid:str):
    # Check if user is owner
    try:
        # print(f"Parsed datas : {userid} and {chatid}")
        foundChat = read_by_id("ChatHistory",chatid)
        # print(foundChat)
        # print(f"User ID : {userid}\nDocument Owner ID : {foundChat.author.author_id}\nIF EQ : {userid == foundChat.author.author_id}")
        if foundChat.author.email == userid.email:
            # Parse the foundChat
            return foundChat
        return create_exception_401
    except Exception as e:
        print(f"Exception : {e}")
        raise create_exception_401

def change_conversation_title(payload:ChatUpdateTitle,userid:dict[str,str]):
    try:
        # found_chat = get_specific_coversation(userid=userid,chatid=payload.id)
        found_chat = read_by_id("ChatHistory",payload.id)
        if found_chat is None:
            return create_exception_401
        if found_chat.author.email != userid.email:
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

def change_specific_message_by_index(payload:ChatUpdateMessageListByIndex,userid:dict[str,str]):
    try:
        # found_chat = get_specific_coversation(userid=userid,chatid=payload.id)
        found_chat = read_by_id("ChatHistory",payload.id)
        if found_chat is None:
            return create_exception_401
        if found_chat.author.email != userid.email:
            return create_exception_401

        updated_chat_history  = update_one(
        "ChatHistory",
        found_chat,
        set__UserQuestions=payload.Chat_UserQuestionList,
        set__MachineAnswers=payload.Chat_MachineAnswerList
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

def change_user_message(payload:ChatUpdateMessage,userid:dict[str,str]):
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

def delete_user_message(id:str,userid:dict[str,str]):
    try:
        found_chat = get_specific_coversation_object(userid=userid,chatid=id)
        delete_one(found_chat)
        return True
    except Exception as e:
        print(f"Error on /edit_message endpoint\n{e}")
        raise create_exception_500

async def append_to_response(userid:dict[str,str],payload:ChatHistoryAppendToEnd):
    """Appends to the existing message and returns the response"""
    """Will be used for append message to existing message endpoint"""
    try:
        objectresult = get_specific_coversation_object(userid=userid,chatid=payload.ChatID)
        userQuestionsList = objectresult['UserQuestions']
        machineAnswersList = objectresult['MachineAnswers']
        # Craft the Question payload
        foundConnectionID = find_connection_id(userid=userid.id)
        user_question_sanitized = sanitize(payload.Question)
        crafted_user_question_with_connectionid = user_question_sanitized + f" . My connection_id : {foundConnectionID.connection_id}"
        # Import agent and preload it with this information
        # result = await agent_awaitrun_with_messages(question=crafted_user_question_with_connectionid,HumanMessages=userQuestionsList,AIMessages=machineAnswersList)
        # Agent does not hold any memory in this
        result = await agent_awaitrun(question=crafted_user_question_with_connectionid)
    except Exception as e:
        print(f"Exception at Append : {e}")
        raise create_exception_500
    print(f"Type payload : {type(result)}\Answer : {result}")
    # Create the payload
    database_payload = ChatHistoryAppend(id=payload.ChatID,UserQuestions=payload.Question,MachineAnswers=result)
    """
    APPEND MESSAGE BACK TO DATABASE UNDER USER QUESTION AND MACHINE ANSWERS
    """
    increment_message_usage(userid=userid.id)
    return append_conversation(payload=database_payload,userid=userid)

async def create_new_response(userid:dict[str,str],payload:Chat_MachineAnswer_single):
    """Creates a new messages and returns the response"""
    """Will be used for Create new message endpoint"""
    # Import agent and preload it with this information
    # Find user from onlizer connect
    try:
        foundConnectionID = find_connection_id(userid=userid.id)
        user_question_sanitized = sanitize(payload.Question)
        # Will be using crafted user question to handle it 
        crafted_user_question_with_connectionid = user_question_sanitized + f" . My connection_id : {foundConnectionID.connection_id}"
        print(f"Question : {crafted_user_question_with_connectionid}")
        # question = {
        #     "input":{
        #         "question": user_question_sanitized,
        #         "connection_id": foundConnectionID.connection_id
        #     }
        # }
        result = await agent_awaitrun(question=crafted_user_question_with_connectionid)
        title = generate_title_ai(question=user_question_sanitized)
    except Exception as e:
        print(f"Exception on Create : {e}")
        raise create_exception_500
    # Create the payload
    payload = ChatHistoryCreate(title=title,UserQuestions=user_question_sanitized,MachineAnswers=result)
    """
    APPEND MESSAGE BACK TO DATABASE UNDER USER QUESTION AND MACHINE ANSWERS
    """
    increment_message_usage(userid=userid.id)
    return add_conversation(payload=payload,userid=userid)

async def regenerate_response(messageIdx:int,userid:dict[str,str],chatid:str):
    """Hypotectically if the message is empty, check for last message to regenerate response, if message index has been given then regenerate the response according to the given index. If index is not given check the last answer and regenerate if it is missing"""
    objectconversation = get_specific_coversation_object(userid=userid,chatid=chatid)
    userQuestionsList = objectconversation['UserQuestions']
    machineAnswersList = objectconversation['MachineAnswers']
    if not messageIdx:
        # Check the length difference
        if len(userQuestionsList) > len(machineAnswersList):
            # use the last question as 
            result = await agent_awaitrun_with_messages(question=userQuestionsList[-1],HumanMessages=userQuestionsList,AIMessages=machineAnswersList)
            machineAnswersList.append(result)
            crafted_payload = ChatUpdateMessageListByIndex(id=chatid,Chat_MachineAnswerList=machineAnswersList,Chat_UserQuestionList=userQuestionsList)
            return change_specific_message_by_index(payload=crafted_payload,userid=userid)
    
    result = await agent_awaitrun_with_messages(question=userQuestionsList[messageIdx],HumanMessages=userQuestionsList[:-messageIdx],AIMessages=machineAnswersList[:-messageIdx])
    machineAnswersList[messageIdx] = result
    crafted_payload = ChatUpdateMessageListByIndex(id=chatid,Chat_MachineAnswerList=machineAnswersList,Chat_UserQuestionList=userQuestionsList)
    return change_specific_message_by_index(payload=crafted_payload,userid=userid)

async def tool_debugger(input):
    return await tool_debug(input=input)

def duckduckgo_search_conversation(Question:str):
    print(f"Calling Conversation DuckDuckGo")
    return duckduckgo_search_agent(Question)
    