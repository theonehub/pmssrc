from fastapi import HTTPException
from models.organisation import Organisation, OrganisationCreate, OrganisationUpdate
from database.database_connector import connect_to_database
import logging
from typing import List, Union
from pydantic import BaseModel

logger = logging.getLogger(__name__)

def get_organisation_collection():
    db = connect_to_database("global_database")
    return db["organisation"]

def get_all_organisations():
    collection = get_organisation_collection()
    cursor = collection.find({"is_active": True});
    organisations = list(cursor)
    for organisation in organisations:
        del organisation["_id"]
    return organisations

def get_organisations_count():
    collection = get_organisation_collection()
    count = collection.count_documents({})
    return count

def get_organisation(organisation_id: str):
    collection = get_organisation_collection()
    organisation = collection.find_one({"organisation_id": organisation_id})
    return organisation

def create_organisation(organisation: OrganisationCreate):
    collection = get_organisation_collection()
    organisation = collection.insert_one(organisation.model_dump())
    return organisation 

def update_organisation(organisation_id: str, organisation: Union[OrganisationUpdate, dict]):
    collection = get_organisation_collection()
    
    # Convert to dict if it's a Pydantic model
    update_data = organisation.model_dump() if hasattr(organisation, 'model_dump') else organisation
    
    # Update the document
    result = collection.update_one(
        {"organisation_id": organisation_id},
        {"$set": update_data}
    )
    
    # Get the updated document
    updated_org = collection.find_one({"organisation_id": organisation_id})
    if "_id" in updated_org:
        del updated_org["_id"]
        
    return updated_org

class OrganisationListResponse(BaseModel):
    organisations: List[Organisation]
    total: int








