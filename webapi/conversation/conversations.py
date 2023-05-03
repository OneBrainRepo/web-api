from webapi.mongo.CRUD import *
from typing import Any

async def get_last_conversation(userid:int) -> (dict[str, str] | dict[str, Any]) :
    """
    Parse user id into the field and return the last messages 
    No datetime just last message
    Id value should be parsed on the routes via jwt claims
    """
    last_question, last_answer = read_last_conversation("ChatHistory", userid)
    if last_question is None:
        return {"last_question":"none","last_answer":"none"}
    return {"last_question":last_question,"last_answer":last_answer}

async def add_conversation():
    pass
    # create("ChatHistory",)