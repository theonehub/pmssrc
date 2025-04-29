from database.database_connector import connect_to_database
from bson import ObjectId
from datetime import datetime
from models.project_attributes import AttributeOut

def get_project_attribute_collection(hostname: str):
    """
    Returns the employee leave collection for the specified company.
    """
    db = connect_to_database(hostname)
    return db["project_attributes"]

def create_attribute(data, hostname):
    project_attribute_collection = get_project_attribute_collection(hostname)
    existing = project_attribute_collection.find_one({"key": data.key})
    if existing:
        raise ValueError("Key already exists")

    attr_dict = data.dict()
    attr_dict["created_at"] = datetime.utcnow()
    result = project_attribute_collection.insert_one(attr_dict)
    return str(result.inserted_id)

def update_attribute(key, update_data, hostname):
    project_attribute_collection = get_project_attribute_collection(hostname)
    result = project_attribute_collection.update_one(
        {"key": key},
        {"$set": update_data.dict(exclude_unset=True)}
    )
    return result.modified_count > 0

def get_all_attributes(hostname):
    project_attribute_collection = get_project_attribute_collection(hostname)
    docs = project_attribute_collection.find()
    return [AttributeOut(**{**doc, "_id": str(doc["_id"])}) for doc in docs]

def get_attribute_by_key(key, hostname):
    project_attribute_collection = get_project_attribute_collection(hostname)
    doc = project_attribute_collection.find_one({"key": key})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def delete_attribute(key, hostname):
    project_attribute_collection = get_project_attribute_collection(hostname)
    return project_attribute_collection.delete_one({"key": key}).deleted_count > 0
