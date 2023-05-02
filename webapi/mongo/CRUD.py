# crud.py
from mongoengine import Document
from typing import Optional
from webapi.mongo.config import connect

# Helper function to get a collection class by name
def get_collection_class(collection_name: str) -> Optional[Document]:
    return globals().get(collection_name.capitalize())

# Create
def create(collection_name: str, **kwargs) -> Optional[Document]:
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass:
        instance = CollectionClass(**kwargs)
        instance.save()
        return instance
    return None

def create_many(collection_name: str, items: list[dict]) -> list[Optional[Document]]:
    return [create(collection_name, **item) for item in items]

# Read
def read(collection_name: str, **filter_kwargs) -> Optional[Document]:
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass:
        return CollectionClass.objects(**filter_kwargs).first()
    return None

def read_many(collection_name: str, **filter_kwargs) -> list[Optional[Document]]:
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass:
        return list(CollectionClass.objects(**filter_kwargs))
    return []

def read_by_filter_and_order(collection_name: str, order: str = '', **filter_kwargs) -> list[Optional[Document]]:
    CollectionClass = get_collection_class(collection_name)
    if CollectionClass:
        return list(CollectionClass.objects(**filter_kwargs).order_by(order))
    return []

# Update
def update_one(collection_name: str, instance: Document, **update_kwargs) -> Optional[Document]:
    if instance:
        instance.update(**update_kwargs)
        instance.reload()
        return instance
    return None

def update_many(collection_name: str, instances: list[Document], **update_kwargs) -> list[Optional[Document]]:
    return [update_one(collection_name, instance, **update_kwargs) for instance in instances]

# Delete
def delete_one(instance: Document) -> None:
    if instance:
        instance.delete()

def delete_many(instances: list[Document]) -> None:
    for instance in instances:
        delete_one(instance)
