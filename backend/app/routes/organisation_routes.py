from fastapi import APIRouter, HTTPException, Depends, Query, status
from services.organisation_service import (
    get_all_organisations as get_all_organisations_service, 
    get_organisation as get_organisation_service, 
    create_organisation as create_organisation_service, 
    update_organisation as update_organisation_service,
    delete_organisation as delete_organisation_service
)
from models.organisation import Organisation, OrganisationCreate, OrganisationUpdate, OrganisationListResponse
from auth.auth import extract_emp_id, extract_role, role_checker
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/organisations", response_model=OrganisationListResponse)
def get_organisations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    current_role: str = Depends(role_checker(["superadmin"]))):
    try:
        organisations = get_all_organisations_service()
        total = len(organisations)
        paginated_organisations = organisations[skip:skip + limit]
        return {
            "organisations": paginated_organisations,
            "total": total
        }
    except Exception as e:
        logger.error(f"Error getting organisations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/organisation/{organisation_id}", response_model=Organisation)
def get_organisation(organisation_id: str,
    current_role: str = Depends(role_checker(["superadmin"]))
                          ):
    try:
        organisation = get_organisation_service(organisation_id)
        return organisation
    except Exception as e:
        logger.error(f"Error getting organisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/organisation", status_code=status.HTTP_201_CREATED)
def create_organisation(organisation: OrganisationCreate,
    current_role: str = Depends(role_checker(["superadmin"]))
                          ):
    try:
        print(organisation)
        create_organisation_service(organisation)
        return {"message": "Organisation created successfully"}
    except Exception as e:
        logger.error(f"Error creating organisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/organisation/{organisation_id}", status_code=status.HTTP_201_CREATED)
def update_organisation(organisation_id: str, organisation: OrganisationUpdate,
    current_role: str = Depends(role_checker(["superadmin"]))
                          ):
    try:
        update_organisation_service(organisation_id, organisation)
        return {"message": "Organisation updated successfully"}
    except Exception as e:
        logger.error(f"Error updating organisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/organisation/{organisation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organisation(organisation_id: str,
    current_role: str = Depends(role_checker(["superadmin"]))
                          ):
    try:
        delete_organisation_service(organisation_id)
        return {"message": "Organisation deleted successfully"} 
    except Exception as e:
        logger.error(f"Error deleting organisation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

