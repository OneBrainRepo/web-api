from webapi.firebase.fb_db import demo_chat_history,demo
from webapi.firebase.firebase_dto import ConversationHistory, DemoUserPass, DemoUser
import datetime
import uuid
import bcrypt

def getLastConversation(userid:int):
    """
    Parse User id from JWT token
    """
    return demo_chat_history.child(userid).order_by_key().limit_to_last(1).get()

def addConversation(userid:int,chatDTO : ConversationHistory):
    """
    Only pass UserID, User Question and Machine Answer
    userid - User ID Foreign Key
    UQuestion - User Question
    MAnswer - Machine Answer
    createdAt - Datetime Default at now
    uuid - Unique ID
    UQuestion:str,MAnswer:str,createdAt:datetime=datetime.now()

    """
    return demo_chat_history.child(userid).push().set(chatDTO.dict())

def getAllConversation(userid:int):
    """
    Returns all conversation done by user
    """
    return demo_chat_history.child(userid).order_by_child("createdAt").get()

def getSpecificConversation(userid:int,uuid:str):
    """
    Returns Specific Conversation by UUID
    """
    return demo_chat_history.child(userid).order_by_child("uuid").equal_to(uuid).get()

def getDemoUser(userDTO:DemoUser) -> bool:
    """
    Get demo user by userid and password, return true or false
    """
    returnedValue = demo.child(userDTO.id).order_by_child("hashval").limit_to_last(1).get()
    return bcrypt.checkpw(userDTO.password.encode('utf-8'),returnedValue["hashval"].encode())

def createDemoUser(userid:int, password:str):
    """
    only for demo, later on email verification an other stuff is required
    """
    mySalt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(password.encode('utf-8'),mySalt)
    UsrObject = DemoUser(id=userid,password=hashed_pwd)
    demo.child(userid).push().set(UsrObject.dict())