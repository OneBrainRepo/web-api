# Firebase DTO part
from pydantic import BaseModel
from datetime import datetime

class DemoUser(BaseModel):
    id : int
    password: str

class DemoUserPass(BaseModel):
    hashval:str
    password: str

class ConversationHistory(BaseModel):
    uuid:str
    user_question:str
    machine_answer: str
    createdAt:datetime