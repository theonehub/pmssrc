from fastapi import APIRouter, HTTPException, Depends, Query
import services.organisation_service as OrganisationService
from models.organisation import Organisation, OrganisationCreate, OrganisationUpdate
from auth.auth import extract_emp_id, extract_role, role_checker
from typing import List

router = APIRouter()

@router.get("/organisations", response_model=List[Organisation])
def get_organisations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    current_role: str = Depends(role_checker(["superadmin"]))
                          ):
    organisations = OrganisationService.get_organisations(skip, limit)
    total = OrganisationService.get_organisations_count()
    return {
        "organisations": organisations,
        "total": total
    }


@router.get("/organisation/{organisation_id}", response_model=Organisation)
def get_organisation(organisation_id: str,
    current_role: str = Depends(role_checker(["superadmin"]))
                          ):
    organisation = OrganisationService.get_organisation(organisation_id)
    return organisation


@router.post("/organisation", response_model=Organisation)
def create_organisation(organisation: OrganisationCreate,
    current_role: str = Depends(role_checker(["superadmin"]))
                          ):
    organisation = OrganisationService.create_organisation(organisation)
    return organisation


@router.put("/organisation/{organisation_id}", response_model=Organisation)
def update_organisation(organisation_id: str, organisation: OrganisationUpdate):
    organisation = OrganisationService.update_organisation(organisation_id, organisation)
    return organisation



