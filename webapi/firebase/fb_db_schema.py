from datetime import datetime
from webapi.firebase.fb_db import demo_chat_history

# Firebase doesnt provide Object Mapper therefore lets define as dictionary then we can find a solution later
def demo_login(id:int, password: str) -> dict:
    """
    This is used when firebase database connection needs to create a new demo_login
    """
    return {
        "id":id,
        "password": password
    }

def chat_history(userid:int,UQuestion:str,MAnswer:str,createdAt:datetime=datetime.now())->list:
    """
    Only pass UserID, User Question and Machine Answer
    userid - User ID Foreign Key
    UQuestion - User Question
    MAnswer - Machine Answer
    createdAt - Datetime Default at now

    returns

    [
        Database Element,
        JSON Object
    ]

    """
    return [
        demo_chat_history.child(userid),
        {
            "user_question":UQuestion,
            "machine_answer": MAnswer,
            "createdAt":createdAt,
        }
    ]
