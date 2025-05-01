from datetime import datetime
import logging
import uuid

from fastapi import HTTPException
from models.organisation import Organisation, OrganisationCreate, OrganisationUpdate
from database.organisation_database import (
    get_all_organisations as db_get_all_organisations,
    create_organisation as db_create_organisation,
    update_organisation as db_update_organisation,
    get_organisation as db_get_organisation,
    get_organisations_count as db_get_organisations_count
)

logger = logging.getLogger(__name__)

def get_all_organisations():
    organisations = db_get_all_organisations()
    return organisations

def get_organisation(organisation_id: str):
    organisation = db_get_organisation(organisation_id)
    return organisation

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
        # Update in database
        updated_org = db_update_organisation(organisation_id, org_dict)
        
        return updated_org
    except Exception as e:
        logger.error(f"Error updating organisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def delete_organisation(organisation_id: str):
    try:
        # Get the organisation
        org = get_organisation(organisation_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organisation not found")
        
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
    
def increment_used_employee_strength(organisation_id: str):
    organisation = get_organisation(organisation_id)
    organisation.used_employee_strength += 1
    update_organisation(organisation_id, organisation)
    return organisation

def decrement_used_employee_strength(organisation_id: str):
    organisation = get_organisation(organisation_id)
    organisation.used_employee_strength -= 1
    update_organisation(organisation_id, organisation)
    return organisation

def get_used_employee_strength(organisation_id: str):
    organisation = get_organisation(organisation_id)
    return organisation.used_employee_strength

def get_employee_strength(organisation_id: str):
    organisation = get_organisation(organisation_id)
    return organisation.employee_strength

def user_creation_allowed(organisation_id: str):
    organisation = get_organisation(organisation_id)
    return organisation.used_employee_strength < organisation.employee_strength