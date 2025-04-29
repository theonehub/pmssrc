from database.database_connector import connect_to_database
from models.reimbursement_type import ReimbursementTypeCreate, ReimbursementTypeUpdate
import uuid
from database.reimbursement_types_database import (
    create_type as db_create_type,
    get_all_types as db_get_all_types,
    update_type as db_update_type,
    delete_type as db_delete_type,
)


def create_type(data: ReimbursementTypeCreate, hostname: str):    
    data.reimbursement_type_id = str(uuid.uuid4())
    return db_create_type(data, hostname)

def get_all_types(hostname: str):
    return db_get_all_types(hostname)

def update_type(type_id: str, data: ReimbursementTypeUpdate, hostname: str):
    return db_update_type(type_id, data, hostname)

def delete_type(type_id: str, hostname: str):
    return db_delete_type(type_id, hostname)
