# crud.py
from mongoengine import Document, ReferenceField, connection
from typing import Optional
from webapi.mongo.config import connect
from webapi.mongo.models import Author, ChatHistory
from bson import ObjectId, json_util
import pydantic
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

# Helper function to get a collection class by name
def get_collection_class(collection_name: str) -> Optional[Document]:
    # print("Printing global keys to find out which is accessible")
    # print(globals().keys())
    # print(f"Get globals {globals().get(collection_name.capitalize())}\nCollection Name as it is {globals().get(collection_name)}")
    # if globals().get(collection_name.capitalize()) is None:
    # return globals().get(collection_name.capitalize())
    return globals().get(collection_name)

# Create
def create(collection_name: str, **kwargs) -> Optional[Document]:
    """
    Example usage

    author = create("Author", name="John Doe", id=1)

    chat1 = create("ChatHistory", title="Chat 1", author=author, UserQuestions=["Question 1"], MachineAnswers=["Answer 1"])
    chat2 = create("ChatHistory", title="Chat 2", author=author, UserQuestions=["Question 2"], MachineAnswers=["Answer 2"])

    """
    # conn = connection.get_connection()
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass:
        instance = CollectionClass(**kwargs)
        print(f"Instance : {instance}\nKwargs : {kwargs}")
        instance.save()
        return instance
    return None

def create_many(collection_name: str, items: list[dict]) -> list[Optional[Document]]:
    """
    authors = create_many("Author", items=[{"name": "Jane Doe", "id": 2}, {"name": "Alice", "id": 3}])
    """
    return [create(collection_name, **item) for item in items]

def createWithReferenceNumber(collection_name: str, **kwargs) -> Optional[Document]:
    """
    Normally if an model holds relation with other we need to parse model itself to ReferenceField
    This method allow us to just parse the `id` value of the author directly to the function and handles everything in the background
    Example use case will be 
    chat_history = create("ChatHistory", title="Sample Chat", author=1, UserQuestions=["What is the meaning of life?"], MachineAnswers=["The meaning of life is a philosophical question."])
    """
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass:
        for key, value in kwargs.items():
            field = CollectionClass._fields.get(key)
            if isinstance(field, ReferenceField) and isinstance(value, (str, int)):
                kwargs[key] = field.document_type.objects(id=value).first()
        instance = CollectionClass(**kwargs)
        instance.save()
        return instance
    return None

# Read
def read(collection_name: str, **filter_kwargs) -> Optional[Document]:
    """
    found_author = read("Author", id=1)
    """
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass:
        return CollectionClass.objects(**filter_kwargs).first()
    return None

def read_many(collection_name: str, **filter_kwargs) -> list[Optional[Document]]:
    """
    found_chats = read_many("ChatHistory", author=author)
    """
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass is None:
        return None
    results = CollectionClass.objects(**filter_kwargs)
    docs = [result.to_mongo().to_dict() for result in results]
        
    return docs

def read_by_filter_and_order(collection_name: str, order: str = '', **filter_kwargs) -> list[Optional[Document]]:
    """
    ordered_chats = read_by_filter_and_order("ChatHistory", order="title", author=author)
    """
    CollectionClass = get_collection_class(collection_name)
    print(f"Collection Class : {CollectionClass}")
    if CollectionClass:
        return list(CollectionClass.objects(**filter_kwargs).order_by(order))
    return []

def read_last_conversation(collection_name: str, author) -> tuple[Optional[str], Optional[str]]:
    """
    Gets the collection name and author id as an argument and returns last user question and machine answer
    It can return a tuple or those two values can be extracted for better use
    Example usage
    last_question, last_answer = read_last_conversation("ChatHistory", author.id)
    """
    print("CHECK THIS")
    CollectionClass = get_collection_class(collection_name)
    print(f"Collection class name : {CollectionClass}")
    if CollectionClass:
        latest_chat = CollectionClass.objects(author=author).order_by('-createdAt').first()
        if latest_chat and latest_chat.UserQuestions and latest_chat.MachineAnswers:
            return latest_chat.UserQuestions[-1], latest_chat.MachineAnswers[-1]
    return None, None

def read_by_id(collection_name: str, obj_id: str) -> Optional[Document]:
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass:
        try:
            return CollectionClass.objects(id=ObjectId(obj_id)).first()
        except Exception as e:
            print(f"Error while reading by ID: {e}")
            return None
    return None

# Update
def update_one(collection_name: str, instance: Document, **update_kwargs) -> Optional[Document]:
    """
    Updates the field by given $set key

    Set key consist of couple things

    set__Field__Index

    set part is required
    Field is the field that would be updated
    Index is the index of the field that would be updated if it is applicable

    Mind the double __ between them

    updated_chat1 = update_one("ChatHistory", chat1, set__MachineAnswers__0="Updated Answer 1")
    """
    if instance:
        instance.update(**update_kwargs)
        instance.reload()
        return instance
    return None

def update_many(collection_name: str, instances: list[Document], **update_kwargs) -> list[Optional[Document]]:
    """
    updated_chats = update_many("ChatHistory", [chat1, chat2], set__title="Updated Title")
    """
    return [update_one(collection_name, instance, **update_kwargs) for instance in instances]

# Delete
def delete_one(instance: Document) -> None:
    """
    Requires the found instance
    """
    if instance:
        instance.delete()

def delete_many(instances: list[Document]) -> None:
    """
    Requires list of parsed documents inside then erases it
    """
    for instance in instances:
        delete_one(instance)
