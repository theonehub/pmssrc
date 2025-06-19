#!/usr/bin/env python3
"""
Migration Scripts for PMS Monolith to Microservices
This script helps migrate data and code from the monolithic application to microservices.
"""

import os
import sys
import argparse
import asyncio
import shutil
from pathlib import Path
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import json
from datetime import datetime

# Configuration
MONOLITH_BACKEND_PATH = "../backend"  # Adjust path to your monolith
SERVICES_PATH = "./services"
SHARED_PATH = "./shared"

# Service mapping - defines what modules belong to which service
SERVICE_MODULE_MAPPING = {
    "user-service": {
        "entities": ["user.py"],
        "use_cases": ["user/"],
        "repositories": ["mongodb_user_repository.py"],
        "routes": ["user_routes_v2.py", "auth_routes_v2.py"],
        "controllers": ["user_controller.py", "auth_controller.py"],
        "dto": ["user_dto.py", "auth_dto.py"],
        "collections": ["users", "user_sessions", "user_permissions"]
    },
    "organization-service": {
        "entities": ["organisation.py"],
        "use_cases": ["organisation/"],
        "repositories": ["mongodb_organisation_repository.py"],
        "routes": ["organisation_routes_v2.py"],
        "controllers": ["organisation_controller.py"],
        "dto": ["organisation_dto.py"],
        "collections": ["organizations", "organization_settings"]
    },
    "leave-service": {
        "entities": ["employee_leave.py", "company_leave.py", "public_holiday.py"],
        "use_cases": ["employee_leave/", "company_leave/", "public_holiday/"],
        "repositories": ["employee_leave_repository_impl.py", "mongodb_company_leave_repository.py", "mongodb_public_holiday_repository.py"],
        "routes": ["employee_leave_routes_v2.py", "leaves_routes_v2.py", "company_leave_routes_v2.py", "public_holiday_routes_v2.py"],
        "controllers": ["employee_leave_controller.py", "company_leave_controller.py", "public_holiday_controller.py"],
        "dto": ["employee_leave_dto.py", "company_leave_dto.py", "public_holiday_dto.py"],
        "collections": ["employee_leaves", "company_leaves", "public_holidays", "leave_policies"]
    },
    "attendance-service": {
        "entities": ["attendance.py"],
        "use_cases": ["attendance/"],
        "repositories": ["mongodb_attendance_repository.py"],
        "routes": ["attendance_routes_v2.py"],
        "controllers": ["attendance_controller.py"],
        "dto": ["attendance_dto.py"],
        "collections": ["attendance_records", "work_schedules", "attendance_analytics"]
    },
    "reimbursement-service": {
        "entities": ["reimbursement.py", "reimbursement_type_entity.py"],
        "use_cases": ["reimbursement/"],
        "repositories": ["mongodb_reimbursement_repository.py"],
        "routes": ["reimbursement_routes_v2.py"],
        "controllers": ["reimbursement_controller.py"],
        "dto": ["reimbursement_dto.py"],
        "collections": ["reimbursement_requests", "reimbursement_types", "reimbursement_receipts"]
    },
    "project-service": {
        "entities": [],  # Project attributes might not have entities
        "use_cases": ["project_attributes/"],
        "repositories": ["project_attributes_repository_impl.py"],
        "routes": ["project_attributes_routes_v2.py"],
        "controllers": ["project_attributes_controller.py"],
        "dto": ["project_attributes_dto.py"],
        "collections": ["project_attributes", "project_configurations"]
    },
    "payroll-service": {
        "entities": ["monthly_salary.py", "employee_salary.py", "periodic_salary_income.py"],
        "use_cases": ["monthly_salary/"],
        "repositories": ["monthly_salary_repository_impl.py"],
        "routes": ["monthly_salary_routes.py", "employee_salary_routes_v2.py"],
        "controllers": ["monthly_salary_controller.py", "payroll_controller.py"],
        "dto": ["monthly_salary_dto.py", "employee_salary_dto.py"],
        "collections": ["monthly_salaries", "salary_components", "payroll_processing"]
    },
    "taxation-service": {
        "entities": ["taxation/"],
        "use_cases": ["taxation/"],
        "repositories": ["taxation/mongodb_taxation_repository.py"],
        "routes": ["taxation_routes.py"],
        "controllers": ["taxation_controller.py"],
        "dto": ["taxation_dto.py"],
        "collections": ["taxation_records", "tax_calculations", "tax_regimes"]
    },
    "reporting-service": {
        "entities": ["report.py"],
        "use_cases": ["reporting/"],
        "repositories": ["mongodb_reporting_repository.py"],
        "routes": ["reporting_routes_v2.py"],
        "controllers": ["reporting_controller.py"],
        "dto": ["reporting_dto.py"],
        "collections": ["aggregated_reports", "analytics_cache", "custom_reports"]
    }
}


class MonolithMigrator:
    """Main migration class"""
    
    def __init__(self, monolith_path: str, services_path: str):
        self.monolith_path = Path(monolith_path)
        self.services_path = Path(services_path)
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
        
    async def migrate_service(self, service_name: str):
        """Migrate a specific service"""
        print(f"\n🚀 Starting migration for {service_name}")
        
        if service_name not in SERVICE_MODULE_MAPPING:
            print(f"❌ Unknown service: {service_name}")
            return False
            
        service_config = SERVICE_MODULE_MAPPING[service_name]
        service_path = self.services_path / service_name
        
        try:
            # 1. Create service directory structure
            self.create_service_structure(service_path)
            
            # 2. Copy and adapt code files
            await self.copy_service_code(service_name, service_config, service_path)
            
            # 3. Create service-specific files
            self.create_service_files(service_name, service_path)
            
            # 4. Migrate database collections
            await self.migrate_database_collections(service_name, service_config)
            
            print(f"✅ Successfully migrated {service_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to migrate {service_name}: {e}")
            return False
    
    def create_service_structure(self, service_path: Path):
        """Create the standard microservice directory structure"""
        directories = [
            "domain/entities",
            "domain/value_objects", 
            "domain/events",
            "application/use_cases",
            "application/dto",
            "application/interfaces",
            "infrastructure/repositories",
            "infrastructure/services",
            "infrastructure/database",
            "api/routes",
            "api/controllers",
            "tests"
        ]
        
        for directory in directories:
            (service_path / directory).mkdir(parents=True, exist_ok=True)
            
        # Create __init__.py files
        for directory in directories:
            (service_path / directory / "__init__.py").touch()
            
        print(f"📁 Created directory structure for {service_path.name}")
    
    async def copy_service_code(self, service_name: str, service_config: dict, service_path: Path):
        """Copy and adapt code files from monolith"""
        
        # Copy entities
        for entity_file in service_config.get("entities", []):
            src = self.monolith_path / "app" / "domain" / "entities" / entity_file
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, service_path / "domain" / "entities" / entity_file, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, service_path / "domain" / "entities" / entity_file)
                print(f"📄 Copied entity: {entity_file}")
        
        # Copy use cases
        for use_case_dir in service_config.get("use_cases", []):
            src = self.monolith_path / "app" / "application" / "use_cases" / use_case_dir
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, service_path / "application" / "use_cases" / use_case_dir, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, service_path / "application" / "use_cases" / use_case_dir.replace("/", ".py"))
                print(f"🔧 Copied use case: {use_case_dir}")
        
        # Copy repositories
        for repo_file in service_config.get("repositories", []):
            src = self.monolith_path / "app" / "infrastructure" / "repositories" / repo_file
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, service_path / "infrastructure" / "repositories" / repo_file, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, service_path / "infrastructure" / "repositories" / repo_file)
                print(f"🗄️ Copied repository: {repo_file}")
        
        # Copy DTOs
        for dto_file in service_config.get("dto", []):
            src = self.monolith_path / "app" / "application" / "dto" / dto_file
            if src.exists():
                shutil.copy2(src, service_path / "application" / "dto" / dto_file)
                print(f"📋 Copied DTO: {dto_file}")
        
        # Copy routes (adapt them for microservice)
        for route_file in service_config.get("routes", []):
            src = self.monolith_path / "app" / "api" / "routes" / route_file
            if src.exists():
                await self.adapt_route_file(src, service_path / "api" / "routes" / route_file, service_name)
                print(f"🛣️ Adapted route: {route_file}")
    
    async def adapt_route_file(self, src_file: Path, dest_file: Path, service_name: str):
        """Adapt route files for microservice architecture"""
        # Read the original route file
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Basic adaptations (you'll need to customize this based on your code)
        adaptations = [
            # Remove dependency container imports
            ("from app.config.dependency_container import", "# from app.config.dependency_container import"),
            
            # Update imports to use local paths
            ("from app.domain", "from domain"),
            ("from app.application", "from application"),
            ("from app.infrastructure", "from infrastructure"),
            
            # Add service-specific dependencies
            (f"# Service: {service_name}", f"# Service: {service_name}\n# TODO: Update dependency injection for microservice"),
        ]
        
        for old, new in adaptations:
            content = content.replace(old, new)
        
        # Write adapted content
        with open(dest_file, 'w') as f:
            f.write(content)
    
    def create_service_files(self, service_name: str, service_path: Path):
        """Create service-specific files (main.py, Dockerfile, etc.)"""
        
        # Create main.py
        main_py_content = f'''"""
{service_name.replace('-', ' ').title()}
"""

import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add shared libraries to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

from common.database import get_database_connector, MongoDBConnector

# Service configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", "{service_name.replace('-', '_')}")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8000))
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

# Global dependencies
db_connector: MongoDBConnector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize service dependencies on startup"""
    global db_connector
    
    # Initialize database connection
    db_connector = get_database_connector(SERVICE_NAME)
    await db_connector.connect(MONGODB_URL)
    
    print(f"✅ {{SERVICE_NAME}} started successfully on port {{SERVICE_PORT}}")
    yield
    
    # Cleanup on shutdown
    if db_connector:
        await db_connector.disconnect()
    print(f"🔴 {{SERVICE_NAME}} shutting down")

# Create FastAPI app
app = FastAPI(
    title="{service_name.replace('-', ' ').title()}",
    description="Microservice for {service_name.replace('-', ' ')} management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{
        "service": SERVICE_NAME,
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected" if db_connector and db_connector.is_connected() else "disconnected"
    }}

@app.get("/")
async def root():
    """Service info endpoint"""
    return {{
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "description": "{service_name.replace('-', ' ').title()} microservice"
    }}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True,
        log_level="info"
    )
'''
        
        with open(service_path / "main.py", 'w') as f:
            f.write(main_py_content)
        
        # Create Dockerfile
        dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../../shared /app/shared
COPY . .

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
'''
        
        with open(service_path / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Create requirements.txt
        requirements_content = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
pymongo==4.6.0
PyJWT==2.8.0
passlib[bcrypt]==1.7.4
httpx==0.25.2
pydantic==2.5.0
structlog==23.2.0
python-dotenv==1.0.0
'''
        
        with open(service_path / "requirements.txt", 'w') as f:
            f.write(requirements_content)
        
        print(f"📝 Created service files for {service_name}")
    
    async def migrate_database_collections(self, service_name: str, service_config: dict):
        """Migrate database collections to service-specific databases"""
        collections = service_config.get("collections", [])
        if not collections:
            return
        
        print(f"🗄️ Migrating database collections for {service_name}")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(self.mongodb_url)
        
        try:
            # Get source database (assuming monolith uses 'pms' database)
            source_db = client["pms_default"]  # Adjust based on your monolith DB name
            
            # Get target database
            target_db_name = f"{service_name.replace('-', '_')}_default"
            target_db = client[target_db_name]
            
            for collection_name in collections:
                print(f"📊 Migrating collection: {collection_name}")
                
                # Check if source collection exists
                if collection_name not in await source_db.list_collection_names():
                    print(f"⚠️ Collection {collection_name} not found in source database")
                    continue
                
                source_collection = source_db[collection_name]
                target_collection = target_db[collection_name]
                
                # Count documents to migrate
                doc_count = await source_collection.count_documents({})
                print(f"📋 Found {doc_count} documents to migrate")
                
                # Migrate in batches
                batch_size = 1000
                migrated = 0
                
                async for doc in source_collection.find():
                    await target_collection.insert_one(doc)
                    migrated += 1
                    
                    if migrated % batch_size == 0:
                        print(f"📈 Migrated {migrated}/{doc_count} documents")
                
                print(f"✅ Completed migration of {collection_name}: {migrated} documents")
        
        finally:
            client.close()
    
    async def migrate_all_services(self):
        """Migrate all services"""
        print("🚀 Starting full migration from monolith to microservices")
        
        success_count = 0
        total_services = len(SERVICE_MODULE_MAPPING)
        
        for service_name in SERVICE_MODULE_MAPPING.keys():
            if await self.migrate_service(service_name):
                success_count += 1
        
        print(f"\n📊 Migration Summary:")
        print(f"✅ Successfully migrated: {success_count}/{total_services} services")
        
        if success_count == total_services:
            print("🎉 All services migrated successfully!")
        else:
            print("⚠️ Some services failed to migrate. Check logs above.")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Migrate PMS monolith to microservices")
    parser.add_argument("--service", help="Specific service to migrate")
    parser.add_argument("--all", action="store_true", help="Migrate all services")
    parser.add_argument("--monolith-path", default=MONOLITH_BACKEND_PATH, help="Path to monolith backend")
    parser.add_argument("--services-path", default=SERVICES_PATH, help="Path to services directory")
    
    args = parser.parse_args()
    
    migrator = MonolithMigrator(args.monolith_path, args.services_path)
    
    if args.all:
        await migrator.migrate_all_services()
    elif args.service:
        await migrator.migrate_service(args.service)
    else:
        print("Please specify --service <service-name> or --all")
        print("Available services:")
        for service_name in SERVICE_MODULE_MAPPING.keys():
            print(f"  - {service_name}")


if __name__ == "__main__":
    asyncio.run(main()) 