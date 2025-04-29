from fastapi import HTTPException
from models.organisation import Organisation, OrganisationCreate, OrganisationUpdate
from database.database_connector import connect_to_database
import logging

logger = logging.getLogger(__name__)

def get_organisation_collection():
    db = connect_to_database("global_database")
    return db["organisation"]

def get_all_organisations():
    collection = get_organisation_collection()
    organisations = collection.find().to_list(length=100)
    return organisations

def get_organisations_count():
    collection = get_organisation_collection()
    count = collection.count_documents({})
    return count

def get_organisation(organisation_id: str):
    collection = get_organisation_collection()
    organisation = collection.find_one({"_id": organisation_id})
    return organisation

def create_organisation(organisation: OrganisationCreate):
    collection = get_organisation_collection()
    organisation = collection.insert_one(organisation.model_dump())
    return organisation 

def update_organisation(organisation_id: str, organisation: OrganisationUpdate):
    collection = get_organisation_collection()
    organisation = collection.update_one({"_id": organisation_id}, {"$set": organisation.model_dump()})
    return organisation








