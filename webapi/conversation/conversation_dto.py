from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatID(BaseModel):
    id: str

class ChatUpdateTitle(BaseModel):
    id:str
    title: str

class ChatUpdateMessage(BaseModel):
    id:ChatID
    Chat_UserQuestion_single: str

class Chat_UserQuestion_single(BaseModel):
    Question: str

class Chat_UserQuestion(BaseModel):
    UserQuestions: List[Chat_UserQuestion_single]

class Chat_MachineAnswer_single(BaseModel):
    Question: str

class Chat_MachineAnswer(BaseModel):
    UserQuestions: List[Chat_MachineAnswer_single]

class ChatHistoryAppend(BaseModel):
    id:str
    UserQuestions:str
    MachineAnswers: str

class ChatUpdateMessageByIndex(BaseModel):
    id:ChatID
    Chat_UserQuestion_single: str
    Chat_MachineAnswer_single: str

class ChatUpdateMessageListByIndex(BaseModel):
    id:ChatID
    Chat_UserQuestionList: list[str]
    Chat_MachineAnswerList: list[str]
class ChatHistoryAppendLatest(BaseModel):
    UserQuestions:str
    MachineAnswers: str

class AuthorDTO(BaseModel):
    id: int
    name: str

class ChatHistoryDTO(BaseModel):
    title: str
    author: AuthorDTO
    UserQuestions: Chat_UserQuestion
    MachineAnswers: Chat_MachineAnswer
    createdAt: datetime
    updatedAt: datetime

class ChatHistoryByID(BaseModel):
    title: str
    author: int
    UserQuestions: Chat_UserQuestion
    MachineAnswers: Chat_MachineAnswer
    createdAt: datetime
    updatedAt: datetime

class ChatHistoryCreate(BaseModel):
    title: str
    UserQuestions: str
    MachineAnswers: str

class MessageWebSocketPayload(BaseModel):
    token: str
    useruui: str
    title: Optional[str]
    UserMessage: str
    messageType: str
    messageuuid : Optional[str]

class ChatHistoryAppendToEnd(BaseModel):
    ChatID: str
    Question: str