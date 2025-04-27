from database.database_connector import reimbursement_types_collection
from models.reimbursement_type import ReimbursementTypeCreate, ReimbursementTypeUpdate
import uuid
from database.reimbursement_types_database import (
    create_type as db_create_type,
    get_all_types as db_get_all_types,
    update_type as db_update_type,
    delete_type as db_delete_type,
)


async def create_type(data: ReimbursementTypeCreate, hostname: str):    
    data.reimbursement_type_id = str(uuid.uuid4())
    return await db_create_type(data, hostname)

async def get_all_types(hostname: str):
    return await db_get_all_types(hostname)

async def update_type(type_id: str, data: ReimbursementTypeUpdate, hostname: str):
    return await db_update_type(type_id, data, hostname)

async def delete_type(type_id: str, hostname: str):
    return await db_delete_type(type_id, hostname)
