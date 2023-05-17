from mongoengine import Document, StringField, ListField, ReferenceField, IntField, DateTimeField, UUIDField
from datetime import datetime
from uuid import uuid4

class Author(Document):
    """
    Author field to check actually which user is communicating with the AI agent
    name - Holds username
    id - Holds userid from SQL database to keep track of the user
    """
    name = StringField(required=True)
    author_id = IntField(required=True)

class ChatHistory(Document):
    """
    Chat History Document to hold conversation between human and AI agent
    title - Chat title / Might be summary of user asked question
    author - Reference to actual Author document
    UserQuestion - List Of User Questions, Index Based
    MachineAnswers - List of Machine Answers, Index Based
    createdAt - Creation Timestamp defaults for datetime.now
    updatedAt - Update timestamp, defaults for None
    """
    chat_id = UUIDField(required=True,default=uuid4)
    title = StringField(required=True)
    author = ReferenceField(Author)
    UserQuestions = ListField(StringField())
    MachineAnswers = ListField(StringField())
    createdAt = DateTimeField(default=datetime.now)
    updatedAt = DateTimeField(default=None)

    def to_mongo(self, *args, **kwargs):
        data = super().to_mongo(*args, **kwargs)
        data["chat_id"] = str(data["chat_id"])
        return data