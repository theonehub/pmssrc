import logging
from pymongo import MongoClient, ASCENDING
from app.config import MONGO_URI

logger = logging.getLogger(__name__)

database_clients = {}

def connect_to_database(company_id: str):
    if company_id not in database_clients:
        client = MongoClient(MONGO_URI, tls=True)
        db_name = "pms_"+company_id
        db = client[db_name]
        database_clients[company_id] = db
        logger.info(f"{db_name} connected and indexes ensured.")
    return database_clients[company_id]

