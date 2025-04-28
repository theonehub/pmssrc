import logging

from fastapi import HTTPException
from models.organisation import Organisation, OrganisationCreate, OrganisationUpdate
from database.organisation_database import (
    get_all_organisations as db_get_all_organisations,
    create_organisation as db_create_organisation,
    update_organisation as db_update_organisation,
)

logger = logging.getLogger(__name__)

async def get_all_organisations(skip: int, limit: int):
    organisations = await db_get_all_organisations(skip, limit)
    total = await db_get_organisations_count()
    return organisations, total 

async def get_organisation(organisation_id: str):
    organisation = await db_get_organisation(organisation_id)
    return organisation

async def create_organisation(organisation: OrganisationCreate):
    organisation = await db_create_organisation(organisation)
    return organisation 

async def update_organisation(organisation_id: str, organisation: OrganisationUpdate):
    organisation = await db_update_organisation(organisation_id, organisation)
    return organisation 

