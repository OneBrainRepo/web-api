from pydantic import BaseModel
from typing import Optional

class AsyncUserQuestionCelery(BaseModel):
    token: str
    useruui: str
    title: Optional[str]
    UserMessage: str
    messageType: str
    messageuuid : Optional[str]