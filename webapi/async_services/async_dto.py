from pydantic import BaseModel

class AsyncUserQuestionCelery(BaseModel):
    token: str
    useruui: str
    title: str
    UserMessage: str
    messageType: str
    messageuuid : str