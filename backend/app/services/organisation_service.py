import logging

from fastapi import HTTPException
from models.organisation import Organisation, OrganisationCreate, OrganisationUpdate
from database.organisation_database import (
    get_all_organisations as db_get_all_organisations,
    create_organisation as db_create_organisation,
    update_organisation as db_update_organisation,
    get_organisation as db_get_organisation,
    get_organisations_count as db_get_organisations_count,
)

logger = logging.getLogger(__name__)

def get_all_organisations(skip: int, limit: int):
    organisations = db_get_all_organisations(skip, limit)
    total = db_get_organisations_count()
    return organisations, total 

def get_organisation(organisation_id: str):
    organisation = db_get_organisation(organisation_id)
    return organisation

def create_organisation(organisation: OrganisationCreate):
    organisation = db_create_organisation(organisation)
    return organisation 

def update_organisation(organisation_id: str, organisation: OrganisationUpdate):
    organisation = db_update_organisation(organisation_id, organisation)
    return organisation 

