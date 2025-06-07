# User Module Architecture Guide
## Reference Implementation for PMS Application Modules

### Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Layer Structure](#layer-structure)
3. [Design Patterns](#design-patterns)
4. [Implementation Guidelines](#implementation-guidelines)
5. [Code Templates](#code-templates)
6. [Best Practices](#best-practices)
7. [Error Handling](#error-handling)
8. [Security & Authentication](#security--authentication)
9. [Testing Strategy](#testing-strategy)
10. [Migration Guide](#migration-guide)

---

## Architecture Overview

The User module implements a **Clean Architecture** with **SOLID principles**, serving as the gold standard for all PMS modules. It follows a layered approach with clear separation of concerns and dependency inversion.

### Core Architectural Principles

1. **Clean Architecture Layers**
   - **Presentation Layer**: Routes and Controllers
   - **Application Layer**: DTOs, Use Cases, and Interfaces
   - **Domain Layer**: Entities, Value Objects, and Domain Services
   - **Infrastructure Layer**: Repositories, External Services, and Database

2. **SOLID Principles Implementation**
   - **S**ingle Responsibility: Each class has one reason to change
   - **O**pen/Closed: Extensible without modification
   - **L**iskov Substitution: Proper interface implementations
   - **I**nterface Segregation: Focused, specific interfaces
   - **D**ependency Inversion: Depends on abstractions

3. **Multi-Tenancy Support**
   - Organisation-based data segregation
   - Hostname-based routing
   - Database per organisation pattern

---

## Layer Structure

### 1. Presentation Layer (`/api/routes/`)

**Purpose**: Handle HTTP requests/responses, input validation, and authentication

```
/api/routes/module_routes_v2.py
├── Route definitions with FastAPI decorators
├── Request/Response models (DTOs)
├── Authentication dependencies
├── Error handling and HTTP status codes
└── Documentation strings
```

**Key Components**:
- Router configuration with prefix and tags
- Dependency injection for controllers
- Authentication middleware integration
- Standardized error responses

### 2. Controller Layer (`/api/controllers/`)

**Purpose**: Orchestrate business operations and handle HTTP-specific concerns

```
/api/controllers/module_controller.py
├── HTTP request orchestration
├── DTO validation and transformation
├── Service layer delegation
├── File upload handling
└── Response formatting
```

**Key Components**:
- Service dependency injection
- Request/response transformation
- File handling coordination
- Error translation to HTTP responses

### 3. Application Layer (`/application/`)

**Purpose**: Define business use cases and application-specific logic

```
/application/
├── dto/module_dto.py              # Data Transfer Objects
├── interfaces/
│   ├── repositories/module_repository.py
│   └── services/module_service.py
└── use_cases/module/
    ├── create_module_use_case.py
    ├── update_module_use_case.py
    └── delete_module_use_case.py
```

**Key Components**:
- Rich DTO classes with validation
- Service and repository interfaces
- Use case implementations
- Business rule validation

### 4. Domain Layer (`/domain/`)

**Purpose**: Core business logic, entities, and domain rules

```
/domain/
├── entities/module.py             # Domain entities
├── value_objects/                 # Value objects
├── domain_services/               # Domain services
└── events/                        # Domain events
```

**Key Components**:
- Rich domain entities with behavior
- Immutable value objects
- Domain-specific business rules
- Event-driven architecture support

### 5. Infrastructure Layer (`/infrastructure/`)

**Purpose**: External concerns, data persistence, and third-party integrations

```
/infrastructure/
├── repositories/mongodb_module_repository.py
├── services/
│   ├── module_service_impl.py
│   ├── notification_service.py
│   └── file_upload_service.py
└── database/
    └── mongodb_connector.py
```

**Key Components**:
- Repository implementations
- Service implementations
- Database connectors
- External API integrations

---

## Design Patterns

### 1. Repository Pattern
```python
# Interface
class ModuleRepository(ABC):
    @abstractmethod
    async def save(self, entity: Module, hostname: str) -> Module:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: ModuleId, hostname: str) -> Optional[Module]:
        pass

# Implementation
class MongoDBModuleRepository(ModuleRepository):
    def __init__(self, database_connector: DatabaseConnector):
        self.db_connector = database_connector
    
    async def save(self, entity: Module, hostname: str) -> Module:
        # Implementation with organisation context
        pass
```

### 2. Service Layer Pattern
```python
class ModuleService(ABC):
    @abstractmethod
    async def create_module(self, request: CreateModuleRequestDTO, current_user: CurrentUser) -> ModuleResponseDTO:
        pass

class ModuleServiceImpl(ModuleService):
    def __init__(self, repository: ModuleRepository, use_cases: ModuleUseCases):
        self.repository = repository
        self.use_cases = use_cases
    
    async def create_module(self, request: CreateModuleRequestDTO, current_user: CurrentUser) -> ModuleResponseDTO:
        return await self.use_cases.create_module.execute(request, current_user)
```

### 3. Use Case Pattern
```python
class CreateModuleUseCase:
    def __init__(self, repository: ModuleRepository, validator: ModuleValidator):
        self.repository = repository
        self.validator = validator
    
    async def execute(self, request: CreateModuleRequestDTO, current_user: CurrentUser) -> ModuleResponseDTO:
        # 1. Validate request
        validation_errors = await self.validator.validate_create_request(request, current_user)
        if validation_errors:
            raise ModuleValidationError("Validation failed", validation_errors)
        
        # 2. Create domain entity
        module = Module.create(
            id=ModuleId(request.id),
            name=request.name,
            # ... other fields
            created_by=current_user.employee_id
        )
        
        # 3. Apply business rules
        business_rule_errors = await self.validator.validate_business_rules(module, current_user)
        if business_rule_errors:
            raise ModuleBusinessRuleError("Business rule violation", business_rule_errors)
        
        # 4. Save entity
        saved_module = await self.repository.save(module, current_user.hostname)
        
        # 5. Return response DTO
        return ModuleResponseDTO.from_entity(saved_module)
```

### 4. DTO Pattern
```python
@dataclass
class CreateModuleRequestDTO:
    """DTO for creating a new module item"""
    
    # Required fields
    name: str
    description: str
    
    # Optional fields with defaults
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    # Audit fields
    created_by: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the request data"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        
        if not self.description or not self.description.strip():
            errors.append("Description is required")
        
        return errors

@dataclass
class ModuleResponseDTO:
    """DTO for module response"""
    
    id: str
    name: str
    description: str
    is_active: bool
    created_at: str
    updated_at: str
    created_by: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity: Module) -> 'ModuleResponseDTO':
        """Create DTO from domain entity"""
        return cls(
            id=str(entity.id.value),
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at.isoformat() if entity.created_at else None,
            updated_at=entity.updated_at.isoformat() if entity.updated_at else None,
            created_by=entity.created_by
        )
```

### 5. Dependency Injection Pattern
```python
class DependencyContainer:
    def __init__(self):
        self._repositories = {}
        self._services = {}
        self._controllers = {}
    
    def get_module_repository(self) -> ModuleRepository:
        if 'module' not in self._repositories:
            self._repositories['module'] = MongoDBModuleRepository(
                self.get_database_connector()
            )
        return self._repositories['module']
    
    def get_module_service(self) -> ModuleService:
        if 'module' not in self._services:
            self._services['module'] = ModuleServiceImpl(
                self.get_module_repository(),
                self.get_notification_service(),
                self.get_file_upload_service()
            )
        return self._services['module']
    
    def get_module_controller(self) -> ModuleController:
        if 'module' not in self._controllers:
            self._controllers['module'] = ModuleController(
                self.get_module_service()
            )
        return self._controllers['module']

# FastAPI dependency functions
def get_module_controller() -> ModuleController:
    container = get_dependency_container()
    return container.get_module_controller()
```

---

## Implementation Guidelines

### 1. Module Creation Checklist

**Step 1: Define Domain Layer**
- [ ] Create domain entity with rich behavior
- [ ] Define value objects for complex types
- [ ] Implement domain services for complex business logic
- [ ] Define domain events if needed

**Step 2: Create Application Layer**
- [ ] Define repository interface
- [ ] Define service interface
- [ ] Create comprehensive DTOs with validation
- [ ] Implement use cases for each business operation
- [ ] Define custom exceptions

**Step 3: Implement Infrastructure Layer**
- [ ] Implement repository with MongoDB
- [ ] Implement service with business logic
- [ ] Add database migrations if needed
- [ ] Integrate with external services

**Step 4: Create Presentation Layer**
- [ ] Define FastAPI routes with proper decorators
- [ ] Implement controller with HTTP concerns
- [ ] Add authentication and authorization
- [ ] Implement comprehensive error handling

**Step 5: Configure Dependencies**
- [ ] Add to dependency container
- [ ] Create FastAPI dependency functions
- [ ] Update main application router

### 2. Naming Conventions

**Files and Directories**:
- Routes: `{module}_routes_v2.py`
- Controllers: `{module}_controller.py`
- Services: `{module}_service_impl.py`
- Repositories: `mongodb_{module}_repository.py`
- DTOs: `{module}_dto.py`
- Entities: `{module}.py`
- Use Cases: `{action}_{module}_use_case.py`

**Classes**:
- DTOs: `{Action}{Module}RequestDTO`, `{Module}ResponseDTO`
- Services: `{Module}ServiceImpl`
- Repositories: `MongoDB{Module}Repository`
- Controllers: `{Module}Controller`
- Entities: `{Module}`
- Use Cases: `{Action}{Module}UseCase`

**Methods**:
- CRUD operations: `create_`, `get_`, `update_`, `delete_`
- Query operations: `find_`, `search_`, `list_`
- Business operations: `approve_`, `reject_`, `activate_`

### 3. Organisation Context Integration

**All operations must include organisation context**:

```python
# Repository methods
async def save(self, entity: Module, hostname: str) -> Module:
    database_name = f"pms_{hostname}"
    # Use organisation-specific database

# Service methods
async def create_module(self, request: CreateModuleRequestDTO, current_user: CurrentUser) -> ModuleResponseDTO:
    # current_user.hostname provides organisation context

# Route handlers
async def create_module(
    request: CreateModuleRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),  # Provides organisation context
    controller: ModuleController = Depends(get_module_controller)
):
    return await controller.create_module(request, current_user)
```

---

## Code Templates

### 1. Route Template
```python
"""
Module API Routes
FastAPI route definitions for module management
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from datetime import datetime

from app.api.controllers.module_controller import ModuleController
from app.application.dto.module_dto import (
    CreateModuleRequestDTO,
    UpdateModuleRequestDTO,
    ModuleSearchFiltersDTO,
    ModuleResponseDTO,
    ModuleListResponseDTO,
    ModuleValidationError,
    ModuleBusinessRuleError,
    ModuleNotFoundError,
    ModuleConflictError
)
from app.auth.auth_dependencies import CurrentUser, get_current_user
from app.config.dependency_container import get_module_controller

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/modules", tags=["modules-v2"])

# Health check endpoint
@router.get("/health")
async def health_check(
    controller: ModuleController = Depends(get_module_controller)
) -> Dict[str, str]:
    """Health check for module service."""
    return {"status": "healthy", "service": "module_service"}

# CRUD endpoints
@router.post("/", response_model=ModuleResponseDTO)
async def create_module(
    request: CreateModuleRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ModuleController = Depends(get_module_controller)
) -> ModuleResponseDTO:
    """Create a new module."""
    try:
        logger.info(f"Creating module by {current_user.employee_id} in organisation {current_user.hostname}")
        return await controller.create_module(request, current_user)
    except ModuleValidationError as e:
        logger.warning(f"Validation error creating module: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    except ModuleConflictError as e:
        logger.warning(f"Conflict error creating module: {e}")
        raise HTTPException(status_code=409, detail={"error": "conflict_error", "message": str(e)})
    except ModuleBusinessRuleError as e:
        logger.warning(f"Business rule error creating module: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error creating module: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=ModuleListResponseDTO)
async def list_modules(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ModuleController = Depends(get_module_controller)
):
    """List modules with optional filters and pagination"""
    try:
        filters = ModuleSearchFiltersDTO(
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=min(limit, 100),
            is_active=is_active,
            sort_by=sort_by or "created_at",
            sort_order=sort_order or "desc"
        )
        
        return await controller.list_modules(filters, current_user)
    except Exception as e:
        logger.error(f"Error listing modules: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{module_id}", response_model=ModuleResponseDTO)
async def get_module(
    module_id: str = Path(..., description="Module ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ModuleController = Depends(get_module_controller)
):
    """Get module by ID"""
    try:
        response = await controller.get_module_by_id(module_id, current_user)
        if not response:
            raise HTTPException(status_code=404, detail="Module not found")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting module {module_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{module_id}", response_model=ModuleResponseDTO)
async def update_module(
    module_id: str = Path(..., description="Module ID"),
    request: UpdateModuleRequestDTO = None,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ModuleController = Depends(get_module_controller)
):
    """Update an existing module"""
    try:
        return await controller.update_module(module_id, request, current_user)
    except ModuleNotFoundError as e:
        logger.warning(f"Module not found for update: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    except ModuleValidationError as e:
        logger.warning(f"Validation error updating module: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    except ModuleConflictError as e:
        logger.warning(f"Conflict error updating module: {e}")
        raise HTTPException(status_code=409, detail={"error": "conflict_error", "message": str(e)})
    except ModuleBusinessRuleError as e:
        logger.warning(f"Business rule error updating module: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error updating module {module_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{module_id}")
async def delete_module(
    module_id: str = Path(..., description="Module ID"),
    force: bool = Query(False, description="Force deletion even if business rules prevent it"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ModuleController = Depends(get_module_controller)
):
    """Delete module"""
    try:
        await controller.delete_module(module_id, force, current_user)
        return {"message": "Module deleted successfully"}
    except ModuleNotFoundError as e:
        logger.warning(f"Module not found for deletion: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    except ModuleBusinessRuleError as e:
        logger.warning(f"Business rule error deleting module: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error deleting module {module_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 2. Controller Template
```python
"""
Module Controller Implementation
SOLID-compliant controller for module HTTP operations
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from app.application.interfaces.services.module_service import ModuleService
from app.application.dto.module_dto import (
    CreateModuleRequestDTO, UpdateModuleRequestDTO, ModuleSearchFiltersDTO,
    ModuleResponseDTO, ModuleListResponseDTO
)
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)

class ModuleController:
    """
    Module controller following SOLID principles.
    
    - SRP: Only handles HTTP request/response concerns
    - OCP: Can be extended with new endpoints
    - LSP: Can be substituted with other controllers
    - ISP: Focused interface for module HTTP operations
    - DIP: Depends on abstractions (ModuleService)
    """
    
    def __init__(self, module_service: ModuleService):
        """Initialize controller with dependencies."""
        self.module_service = module_service
    
    async def create_module(
        self, 
        request: CreateModuleRequestDTO, 
        current_user: CurrentUser
    ) -> ModuleResponseDTO:
        """Create a new module."""
        try:
            logger.info(f"Creating module in organisation: {current_user.hostname}")
            return await self.module_service.create_module(request, current_user)
        except Exception as e:
            logger.error(f"Error creating module in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_module_by_id(
        self, 
        module_id: str, 
        current_user: CurrentUser
    ) -> ModuleResponseDTO:
        """Get module by ID."""
        try:
            module = await self.module_service.get_module_by_id(module_id, current_user)
            if not module:
                raise HTTPException(status_code=404, detail="Module not found")
            return module
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting module {module_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def list_modules(
        self, 
        filters: ModuleSearchFiltersDTO, 
        current_user: CurrentUser
    ) -> ModuleListResponseDTO:
        """List modules with filters."""
        try:
            return await self.module_service.list_modules(filters, current_user)
        except Exception as e:
            logger.error(f"Error listing modules in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def update_module(
        self,
        module_id: str,
        request: UpdateModuleRequestDTO,
        current_user: CurrentUser
    ) -> ModuleResponseDTO:
        """Update module."""
        try:
            return await self.module_service.update_module(module_id, request, current_user)
        except Exception as e:
            logger.error(f"Error updating module {module_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def delete_module(
        self,
        module_id: str,
        force: bool,
        current_user: CurrentUser
    ) -> bool:
        """Delete module."""
        try:
            return await self.module_service.delete_module(module_id, force, current_user)
        except Exception as e:
            logger.error(f"Error deleting module {module_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
```

### 3. Service Template
```python
"""
Module Service Implementation
SOLID-compliant implementation of module service interface
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.application.interfaces.services.module_service import ModuleService
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.use_cases.module.create_module_use_case import CreateModuleUseCase
from app.application.use_cases.module.update_module_use_case import UpdateModuleUseCase
from app.application.use_cases.module.delete_module_use_case import DeleteModuleUseCase
from app.application.dto.module_dto import (
    CreateModuleRequestDTO, UpdateModuleRequestDTO, ModuleSearchFiltersDTO,
    ModuleResponseDTO, ModuleListResponseDTO, ModuleSummaryDTO
)
from app.domain.entities.module import Module
from app.domain.value_objects.module_id import ModuleId
from app.infrastructure.services.notification_service import NotificationService
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)

class ModuleServiceImpl(ModuleService):
    """
    Complete implementation of module service interface.
    
    Follows SOLID principles:
    - SRP: Delegates to specific use cases and services
    - OCP: Extensible through dependency injection
    - LSP: Implements all interface contracts correctly
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        module_repository: ModuleRepository,
        notification_service: NotificationService
    ):
        """Initialize service with dependencies."""
        self.module_repository = module_repository
        self.notification_service = notification_service
        
        # Initialize use cases
        self._create_module_use_case = CreateModuleUseCase(
            module_repository, self
        )
        self._update_module_use_case = UpdateModuleUseCase(
            module_repository, self
        )
        self._delete_module_use_case = DeleteModuleUseCase(
            module_repository, self
        )
    
    async def create_module(
        self, 
        request: CreateModuleRequestDTO, 
        current_user: CurrentUser
    ) -> ModuleResponseDTO:
        """Create a new module."""
        try:
            logger.info(f"Creating module in organisation: {current_user.hostname}")
            return await self._create_module_use_case.execute(request, current_user)
        except Exception as e:
            logger.error(f"Error creating module in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_module_by_id(
        self, 
        module_id: str, 
        current_user: CurrentUser
    ) -> Optional[ModuleResponseDTO]:
        """Get module by ID."""
        try:
            module = await self.module_repository.get_by_id(
                ModuleId(module_id), 
                current_user.hostname
            )
            if not module:
                return None
            return ModuleResponseDTO.from_entity(module)
        except Exception as e:
            logger.error(f"Error getting module {module_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def list_modules(
        self, 
        filters: ModuleSearchFiltersDTO, 
        current_user: CurrentUser
    ) -> ModuleListResponseDTO:
        """List modules with filters."""
        try:
            modules, total_count = await self.module_repository.find_with_filters(
                filters, current_user.hostname
            )
            
            module_summaries = [
                ModuleSummaryDTO.from_entity(module) for module in modules
            ]
            
            total_pages = (total_count + filters.page_size - 1) // filters.page_size
            
            return ModuleListResponseDTO(
                modules=module_summaries,
                total_count=total_count,
                page=filters.page,
                page_size=filters.page_size,
                total_pages=total_pages,
                has_next=filters.page < total_pages,
                has_previous=filters.page > 1
            )
        except Exception as e:
            logger.error(f"Error listing modules in organisation {current_user.hostname}: {e}")
            raise
    
    async def update_module(
        self,
        module_id: str,
        request: UpdateModuleRequestDTO,
        current_user: CurrentUser
    ) -> ModuleResponseDTO:
        """Update module."""
        try:
            return await self._update_module_use_case.execute(module_id, request, current_user)
        except Exception as e:
            logger.error(f"Error updating module {module_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def delete_module(
        self,
        module_id: str,
        force: bool,
        current_user: CurrentUser
    ) -> bool:
        """Delete module."""
        try:
            return await self._delete_module_use_case.execute(module_id, force, current_user)
        except Exception as e:
            logger.error(f"Error deleting module {module_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def send_module_created_notification(self, module: Module) -> bool:
        """Send notification when module is created."""
        try:
            # Implementation for sending notifications
            return True
        except Exception as e:
            logger.error(f"Error sending module created notification: {e}")
            return False
```

### 4. Repository Template
```python
"""
MongoDB Module Repository Implementation
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime

from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.dto.module_dto import ModuleSearchFiltersDTO
from app.domain.entities.module import Module
from app.domain.value_objects.module_id import ModuleId
from app.infrastructure.database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)

class MongoDBModuleRepository(ModuleRepository):
    """
    MongoDB implementation of module repository.
    
    Handles organisation-based data segregation through database selection.
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """Initialize repository with database connector."""
        self.db_connector = database_connector
        self.collection_name = "modules"
    
    async def save(self, module: Module, hostname: str) -> Module:
        """Save module to organisation-specific database."""
        try:
            database_name = f"pms_{hostname}"
            db = await self.db_connector.get_database(database_name)
            collection = db[self.collection_name]
            
            module_dict = self._entity_to_dict(module)
            
            if module.is_new():
                # Insert new module
                result = await collection.insert_one(module_dict)
                module_dict["_id"] = result.inserted_id
            else:
                # Update existing module
                await collection.replace_one(
                    {"id": module.id.value},
                    module_dict
                )
            
            return self._dict_to_entity(module_dict)
            
        except Exception as e:
            logger.error(f"Error saving module to database {hostname}: {e}")
            raise
    
    async def get_by_id(self, module_id: ModuleId, hostname: str) -> Optional[Module]:
        """Get module by ID from organisation-specific database."""
        try:
            database_name = f"pms_{hostname}"
            db = await self.db_connector.get_database(database_name)
            collection = db[self.collection_name]
            
            module_dict = await collection.find_one({"id": module_id.value})
            
            if not module_dict:
                return None
            
            return self._dict_to_entity(module_dict)
            
        except Exception as e:
            logger.error(f"Error getting module {module_id.value} from database {hostname}: {e}")
            raise
    
    async def find_with_filters(
        self, 
        filters: ModuleSearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[Module], int]:
        """Find modules with filters from organisation-specific database."""
        try:
            database_name = f"pms_{hostname}"
            db = await self.db_connector.get_database(database_name)
            collection = db[self.collection_name]
            
            # Build query
            query = {}
            if filters.is_active is not None:
                query["is_active"] = filters.is_active
            
            # Count total documents
            total_count = await collection.count_documents(query)
            
            # Build sort criteria
            sort_criteria = []
            if filters.sort_by:
                sort_direction = 1 if filters.sort_order == "asc" else -1
                sort_criteria.append((filters.sort_by, sort_direction))
            
            # Calculate skip
            skip = (filters.page - 1) * filters.page_size
            
            # Execute query
            cursor = collection.find(query).sort(sort_criteria).skip(skip).limit(filters.page_size)
            module_dicts = await cursor.to_list(length=filters.page_size)
            
            modules = [self._dict_to_entity(module_dict) for module_dict in module_dicts]
            
            return modules, total_count
            
        except Exception as e:
            logger.error(f"Error finding modules with filters in database {hostname}: {e}")
            raise
    
    async def delete(self, module_id: ModuleId, hostname: str) -> bool:
        """Delete module from organisation-specific database."""
        try:
            database_name = f"pms_{hostname}"
            db = await self.db_connector.get_database(database_name)
            collection = db[self.collection_name]
            
            result = await collection.delete_one({"id": module_id.value})
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting module {module_id.value} from database {hostname}: {e}")
            raise
    
    def _entity_to_dict(self, module: Module) -> dict:
        """Convert module entity to dictionary."""
        return {
            "id": module.id.value,
            "name": module.name,
            "description": module.description,
            "is_active": module.is_active,
            "created_at": module.created_at,
            "updated_at": module.updated_at,
            "created_by": module.created_by,
            "updated_by": module.updated_by
        }
    
    def _dict_to_entity(self, module_dict: dict) -> Module:
        """Convert dictionary to module entity."""
        return Module(
            id=ModuleId(module_dict["id"]),
            name=module_dict["name"],
            description=module_dict["description"],
            is_active=module_dict.get("is_active", True),
            created_at=module_dict.get("created_at"),
            updated_at=module_dict.get("updated_at"),
            created_by=module_dict.get("created_by"),
            updated_by=module_dict.get("updated_by")
        )
```

---

## Best Practices

### 1. Error Handling
- Use custom domain exceptions
- Implement proper HTTP status codes
- Provide detailed error messages
- Log errors with context

### 2. Validation
- Validate at DTO level
- Implement business rule validation
- Use type hints consistently
- Provide meaningful error messages

### 3. Security
- Always include organisation context
- Implement role-based access control
- Validate user permissions
- Sanitize input data

### 4. Performance
- Use pagination for list operations
- Implement proper indexing
- Use async/await consistently
- Cache frequently accessed data

### 5. Testing
- Write unit tests for each layer
- Mock external dependencies
- Test error scenarios
- Use integration tests for workflows

---

## Error Handling

### Custom Exception Hierarchy
```python
class ModuleError(Exception):
    """Base exception for module operations."""
    pass

class ModuleValidationError(ModuleError):
    """Raised when module validation fails."""
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []

class ModuleBusinessRuleError(ModuleError):
    """Raised when business rule validation fails."""
    def __init__(self, message: str, rule: str = None):
        super().__init__(message)
        self.rule = rule

class ModuleNotFoundError(ModuleError):
    """Raised when module is not found."""
    def __init__(self, module_id: str):
        super().__init__(f"Module not found: {module_id}")
        self.module_id = module_id

class ModuleConflictError(ModuleError):
    """Raised when module operation conflicts with existing data."""
    def __init__(self, message: str, conflict_field: str = None):
        super().__init__(message)
        self.conflict_field = conflict_field
```

### HTTP Error Mapping
```python
# In routes
try:
    return await controller.create_module(request, current_user)
except ModuleValidationError as e:
    raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e), "errors": e.errors})
except ModuleConflictError as e:
    raise HTTPException(status_code=409, detail={"error": "conflict_error", "message": str(e)})
except ModuleBusinessRuleError as e:
    raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
except ModuleNotFoundError as e:
    raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Security & Authentication

### Organisation Context
```python
# All operations must include organisation context
async def create_module(
    request: CreateModuleRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),  # Provides hostname
    controller: ModuleController = Depends(get_module_controller)
):
    # current_user.hostname is used for database selection
    return await controller.create_module(request, current_user)
```

### Role-Based Access Control
```python
from app.auth.auth_dependencies import require_role

@router.post("/admin-only")
async def admin_only_operation(
    current_user: CurrentUser = Depends(require_role("admin")),
    controller: ModuleController = Depends(get_module_controller)
):
    # Only admin users can access this endpoint
    pass
```

### Permission-Based Access Control
```python
from app.auth.auth_dependencies import require_permission

@router.delete("/{module_id}")
async def delete_module(
    module_id: str,
    current_user: CurrentUser = Depends(require_permission("module:delete")),
    controller: ModuleController = Depends(get_module_controller)
):
    # Only users with module:delete permission can access
    pass
```

---

## Testing Strategy

### Unit Tests
```python
import pytest
from unittest.mock import Mock, AsyncMock
from app.application.use_cases.module.create_module_use_case import CreateModuleUseCase
from app.application.dto.module_dto import CreateModuleRequestDTO

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_validator():
    return Mock()

@pytest.fixture
def create_module_use_case(mock_repository, mock_validator):
    return CreateModuleUseCase(mock_repository, mock_validator)

@pytest.mark.asyncio
async def test_create_module_success(create_module_use_case, mock_repository, mock_validator):
    # Arrange
    request = CreateModuleRequestDTO(name="Test Module", description="Test Description")
    current_user = Mock()
    current_user.hostname = "test_org"
    current_user.employee_id = "EMP001"
    
    mock_validator.validate_create_request = AsyncMock(return_value=[])
    mock_validator.validate_business_rules = AsyncMock(return_value=[])
    mock_repository.save = AsyncMock(return_value=Mock())
    
    # Act
    result = await create_module_use_case.execute(request, current_user)
    
    # Assert
    assert result is not None
    mock_repository.save.assert_called_once()
```

### Integration Tests
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_module_integration():
    # Test the full flow from HTTP request to database
    response = client.post(
        "/api/v2/modules/",
        json={"name": "Test Module", "description": "Test Description"},
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Module"
```

---

## Migration Guide

### From Existing Module to User Module Architecture

**Step 1: Analyze Current Implementation**
- Identify existing layers and components
- Map current functionality to new architecture
- Identify missing components

**Step 2: Create Migration Plan**
- Plan incremental migration steps
- Identify breaking changes
- Plan data migration if needed

**Step 3: Implement New Architecture**
- Start with domain layer (entities, value objects)
- Add application layer (DTOs, interfaces, use cases)
- Implement infrastructure layer (repositories, services)
- Update presentation layer (routes, controllers)

**Step 4: Update Dependencies**
- Add to dependency container
- Update route registration
- Update tests

**Step 5: Validate Migration**
- Run comprehensive tests
- Validate all functionality works
- Performance testing
- Security validation

### Backward Compatibility
- Maintain existing API endpoints during transition
- Use adapter pattern for legacy integration
- Gradual migration of clients
- Deprecation notices for old endpoints

---

## Conclusion

This architecture guide provides a comprehensive foundation for implementing robust, scalable, and maintainable modules in the PMS application. By following these patterns and practices, you ensure:

1. **Consistency** across all modules
2. **Maintainability** through clean architecture
3. **Scalability** through proper separation of concerns
4. **Security** through organisation context and RBAC
5. **Testability** through dependency injection and mocking
6. **Performance** through proper data access patterns

Use this guide as a reference when creating new modules or enhancing existing ones to maintain architectural consistency and quality standards.

---

## Quick Reference

### Key Files to Create for New Module:
1. `backend/app/api/routes/{module}_routes_v2.py`
2. `backend/app/api/controllers/{module}_controller.py`
3. `backend/app/application/dto/{module}_dto.py`
4. `backend/app/application/interfaces/repositories/{module}_repository.py`
5. `backend/app/application/interfaces/services/{module}_service.py`
6. `backend/app/application/use_cases/{module}/create_{module}_use_case.py`
7. `backend/app/domain/entities/{module}.py`
8. `backend/app/infrastructure/repositories/mongodb_{module}_repository.py`
9. `backend/app/infrastructure/services/{module}_service_impl.py`

### Key Patterns to Follow:
- Always include `current_user: CurrentUser` parameter for organisation context
- Use custom exceptions for domain-specific errors
- Implement comprehensive DTO validation
- Follow naming conventions consistently
- Include proper logging and error handling
- Write tests for each layer

### Remember:
- Organisation context is mandatory for all operations
- Use dependency injection for all components
- Follow SOLID principles in all implementations
- Implement proper error handling and logging
- Write comprehensive tests
- Document all public APIs 