from datetime import datetime
import logging
import uuid

from fastapi import HTTPException
from models.organisation import Organisation, OrganisationCreate, OrganisationUpdate
from database.organisation_database import (
    get_all_organisations as db_get_all_organisations,
    create_organisation as db_create_organisation,
    update_organisation as db_update_organisation,
    get_organisation_by_id as db_get_organisation_by_id,
    get_organisations_count as db_get_organisations_count,
    get_organisation_by_hostname as db_get_organisation_by_hostname
)

logger = logging.getLogger(__name__)


def get_all_organisations():
    organisations = db_get_all_organisations()
    return organisations

def get_organisation_by_id(organisation_id: str):
    organisation_data = db_get_organisation_by_id(organisation_id)
    if organisation_data is None:
        return None
    # Convert the MongoDB document to an Organisation object
    return Organisation(**organisation_data)

def get_organisation_by_hostname(hostname: str):
    organisation_data = db_get_organisation_by_hostname(hostname)
    if organisation_data is None:
        return None
    # Convert the MongoDB document to an Organisation object
    return Organisation(**organisation_data)

def create_organisation(organisation: OrganisationCreate):
    try:
        organisation.organisation_id = str(uuid.uuid4())
        organisation.created_at = datetime.now()
        organisation.updated_at = datetime.now()
        created_org = db_create_organisation(organisation)
        
        return created_org
    except Exception as e:
        logger.error(f"Error creating organisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def update_organisation(organisation_id: str, organisation: OrganisationUpdate):
    try:
        updated_org = db_update_organisation(organisation_id, organisation)
        return updated_org
    except Exception as e:
        logger.error(f"Error updating organisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def delete_organisation(organisation_id: str):
    try:
        # Get the organisation
        org = get_organisation_by_id(organisation_id)
        if not org:
            raise HTTPException(status_code=404, detail="delete_organisation Organisation not found")
        
        # Create update data
        update_data = {
            "is_active": False,
            "updated_at": datetime.now()
        }
        
        # Update in database
        updated_org = db_update_organisation(organisation_id, update_data)
        
        return {"message": "Organisation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting organisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
    
def increment_used_employee_strength(hostname: str):
    organisation = get_organisation_by_hostname(hostname)
    if organisation is None:
        raise HTTPException(status_code=404, detail="increment_used_employee_strength Organisation not found")
    print(organisation)
    organisation.used_employee_strength += 1
    update_organisation(organisation.organisation_id, organisation)
    return organisation

def decrement_used_employee_strength(hostname: str):
    organisation = get_organisation_by_hostname(hostname)
    if organisation is None:
        raise HTTPException(status_code=404, detail="decrement_used_employee_strength Organisation not found")
    organisation.used_employee_strength -= 1
    update_organisation(organisation.organisation_id, organisation)
    return organisation

def get_used_employee_strength(hostname: str):
    organisation = get_organisation_by_hostname(hostname)
    if organisation is None:
        raise HTTPException(status_code=404, detail="get_used_employee_strength Organisation not found")
    return organisation.used_employee_strength

def get_employee_strength(hostname: str):
    organisation = get_organisation_by_hostname(hostname)
    if organisation is None:
        raise HTTPException(status_code=404, detail="get_employee_strength Organisation not found")
    return organisation.employee_strength

def user_creation_allowed(hostname: str):
    organisation = get_organisation_by_hostname(hostname)
    if organisation is None:
        raise HTTPException(status_code=404, detail="user_creation_allowed Organisation not found")
    return organisation.used_employee_strength < organisation.employee_strength

def is_govt_organisation(hostname: str):
    organisation = get_organisation_by_hostname(hostname)
    if organisation is None:
        raise HTTPException(status_code=404, detail="is_govt_organisation Organisation not found")
    return organisation.is_govt_organisation

