from database.database_connector import project_attribute_collection
from bson import ObjectId
from datetime import datetime
from models.project_attributes import AttributeOut

def create_attribute(data):
    existing = project_attribute_collection.find_one({"key": data.key})
    if existing:
        raise ValueError("Key already exists")

    attr_dict = data.dict()
    attr_dict["created_at"] = datetime.utcnow()
    result = project_attribute_collection.insert_one(attr_dict)
    return str(result.inserted_id)

def update_attribute(key, update_data):
    result = project_attribute_collection.update_one(
        {"key": key},
        {"$set": update_data.dict(exclude_unset=True)}
    )
    return result.modified_count > 0

def get_all_attributes():
    docs = project_attribute_collection.find()
    return [AttributeOut(**{**doc, "_id": str(doc["_id"])}) for doc in docs]

def get_attribute_by_key(key):
    doc = project_attribute_collection.find_one({"key": key})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def delete_attribute(key):
    return project_attribute_collection.delete_one({"key": key}).deleted_count > 0
