# Company Leave Management System - Complete Implementation Guide

## Overview

This document provides a comprehensive guide to the Company Leave Management System implementation, which follows Clean Architecture principles and SOLID design patterns. The system provides end-to-end functionality for managing company leave policies with MongoDB persistence and FastAPI REST endpoints.

## Architecture Overview

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Controllers                            │   │
│  │  • CompanyLeaveController                          │   │
│  │  • HTTP Request/Response handling                  │   │
│  │  • Authentication & Authorization                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 Application Layer                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                Use Cases                            │   │
│  │  • CreateCompanyLeaveUseCase                       │   │
│  │  • GetCompanyLeavesUseCase                         │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   DTOs                              │   │
│  │  • CompanyLeaveCreateRequestDTO                    │   │
│  │  • CompanyLeaveResponseDTO                         │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Repository Interfaces                  │   │
│  │  • CompanyLeaveCommandRepository                   │   │
│  │  • CompanyLeaveQueryRepository                     │   │
│  │  • CompanyLeaveAnalyticsRepository                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Domain Layer                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Entities                            │   │
│  │  • CompanyLeave (Aggregate Root)                   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Value Objects                          │   │
│  │  • LeaveType                                       │   │
│  │  • LeavePolicy                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               Domain Events                         │   │
│  │  • CompanyLeaveCreated                             │   │
│  │  • CompanyLeaveUpdated                             │   │
│  │  • CompanyLeavePolicyChanged                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Repository Implementations               │   │
│  │  • MongoDBCompanyLeaveCommandRepository           │   │
│  │  • MongoDBCompanyLeaveQueryRepository             │   │
│  │  • MongoDBCompanyLeaveAnalyticsRepository         │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             Service Implementations                 │   │
│  │  • MongoDBEventPublisher                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
backend/app/
├── api/
│   └── controllers/
│       └── company_leave_controller.py      # FastAPI REST endpoints
├── application/
│   ├── dto/
│   │   └── company_leave_dto.py             # Data Transfer Objects
│   ├── interfaces/
│   │   └── repositories/
│   │       └── company_leave_repository.py  # Repository interfaces
│   └── use_cases/
│       └── company_leave/
│           ├── create_company_leave_use_case.py
│           └── get_company_leaves_use_case.py
├── domain/
│   ├── entities/
│   │   └── company_leave.py                 # Aggregate root
│   ├── events/
│   │   └── leave_events.py                  # Domain events
│   └── value_objects/
│       ├── leave_type.py                    # Leave type value object
│       └── leave_policy.py                  # Leave policy value object
└── infrastructure/
    ├── repositories/
    │   └── mongodb_company_leave_repository.py  # MongoDB implementations
    └── services/
        └── mongodb_event_publisher.py           # Event publisher
```

## Key Components

### 1. Domain Layer

#### Value Objects

**LeaveType** (`domain/value_objects/leave_type.py`)
- Immutable representation of leave types
- Enums for categories and accrual types
- Factory methods for common leave types
- Business logic for validation

```python
# Example usage
casual_leave = LeaveType.casual_leave()
sick_leave = LeaveType.sick_leave()
annual_leave = LeaveType.annual_leave()
```

**LeavePolicy** (`domain/value_objects/leave_policy.py`)
- Complex policy configuration with 15+ parameters
- Accrual, application, approval, and encashment rules
- Business logic for calculations and validation

```python
# Example usage
policy = LeavePolicy.casual_leave_policy(annual_allocation=12)
```

#### Entities

**CompanyLeave** (`domain/entities/company_leave.py`)
- Aggregate root for company leave management
- Factory methods for creation
- Business rule enforcement
- Domain event generation

```python
# Example usage
company_leave = CompanyLeave.create_casual_leave(
    annual_allocation=12,
    created_by="admin"
)
```

#### Domain Events

**Leave Events** (`domain/events/leave_events.py`)
- 13 event types covering all business scenarios
- Rich event data with business context
- Event registry for type lookup

### 2. Application Layer

#### Use Cases

**CreateCompanyLeaveUseCase**
- 8-step workflow for creating company leaves
- Comprehensive validation and business rule enforcement
- Event publishing and notification integration

**GetCompanyLeavesUseCase**
- Multiple retrieval methods with filtering
- Statistics generation and analytics
- Search functionality

#### DTOs

**CompanyLeaveCreateRequestDTO**
- 20+ configurable fields with validation
- Dictionary conversion methods
- Custom exception types

### 3. Infrastructure Layer

#### MongoDB Repositories

**Command Repository**
- Write operations (save, update, delete)
- Index management
- Entity-to-document conversion

**Query Repository**
- Read operations with filtering
- Complex queries for employee applicability
- Document-to-entity conversion

**Analytics Repository**
- Aggregation pipelines for reporting
- Usage statistics and compliance reports
- Trend analysis

#### Event Publisher

**MongoDBEventPublisher**
- Event persistence in MongoDB
- In-memory subscription management
- Batch publishing support
- Event history retrieval

### 4. API Layer

#### CompanyLeaveController

**Endpoints:**
- `POST /api/v1/company-leaves/` - Create company leave
- `GET /api/v1/company-leaves/` - Get all company leaves
- `GET /api/v1/company-leaves/active` - Get active leaves
- `GET /api/v1/company-leaves/{id}` - Get by ID
- `GET /api/v1/company-leaves/type/{code}` - Get by type code
- `GET /api/v1/company-leaves/applicable/employee` - Get applicable leaves
- `GET /api/v1/company-leaves/options/leave-types` - Get options
- `GET /api/v1/company-leaves/statistics/overview` - Get statistics
- `GET /api/v1/company-leaves/search` - Search with filters

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- Each class has a single, well-defined responsibility
- Repositories separated by operation type (Command/Query/Analytics)
- DTOs focused on specific data transfer scenarios

### Open/Closed Principle (OCP)
- Extensible through enums and composition
- New leave types and policies can be added without modification
- Plugin architecture for new features

### Liskov Substitution Principle (LSP)
- Repository implementations are interchangeable
- Value objects maintain contracts across implementations
- Use cases can be substituted with enhanced versions

### Interface Segregation Principle (ISP)
- Focused interfaces for specific operations
- DTOs contain only relevant fields
- Separated concerns in repository interfaces

### Dependency Inversion Principle (DIP)
- Constructor dependency injection throughout
- Dependencies on abstractions, not concretions
- High testability with easy mocking

## Business Features

### Policy Management
- **Accrual Types**: Immediate, monthly, quarterly, annually
- **Carryover Rules**: Maximum days, expiry tracking
- **Approval Workflow**: Auto-approval thresholds, manual approval
- **Medical Certificates**: Required for certain leave types/durations
- **Encashment**: Configurable encashment rules and limits
- **Employee Eligibility**: Gender, category, probation status filtering

### Leave Categories
- **Annual Leave**: Vacation and personal time off
- **Sick Leave**: Medical reasons and health issues
- **Casual Leave**: Personal emergencies and short-term needs
- **Maternity/Paternity Leave**: Parental leave policies
- **Emergency Leave**: Urgent personal situations
- **Bereavement Leave**: Family loss and mourning
- **Study Leave**: Educational and training purposes

### Advanced Features
- **Gender-Specific Policies**: Maternity, paternity leave
- **Probation Restrictions**: Different rules for probationary employees
- **Category-Specific Rules**: Different policies by employee category
- **Advance Notice Requirements**: Minimum notice periods
- **Continuous Days Limits**: Maximum consecutive leave days
- **Medical Certificate Thresholds**: Required documentation

## Database Schema

### MongoDB Collections

**company_leaves**
```json
{
  "_id": ObjectId,
  "company_leave_id": "string",
  "leave_type": {
    "code": "string",
    "name": "string", 
    "category": "string",
    "description": "string"
  },
  "policy": {
    "annual_allocation": "number",
    "accrual_type": "string",
    "accrual_rate": "number",
    "max_carryover_days": "number",
    "carryover_expiry_months": "number",
    "min_advance_notice_days": "number",
    "max_advance_application_days": "number",
    "min_application_days": "number",
    "max_continuous_days": "number",
    "requires_approval": "boolean",
    "auto_approve_threshold": "number",
    "requires_medical_certificate": "boolean",
    "medical_certificate_threshold": "number",
    "is_encashable": "boolean",
    "max_encashment_days": "number",
    "encashment_percentage": "number",
    "available_during_probation": "boolean",
    "probation_allocation": "number",
    "gender_specific": "string",
    "employee_category_specific": "array"
  },
  "is_active": "boolean",
  "description": "string",
  "effective_from": "date",
  "effective_until": "date",
  "created_at": "date",
  "updated_at": "date",
  "created_by": "string",
  "updated_by": "string"
}
```

**domain_events**
```json
{
  "_id": ObjectId,
  "event_type": "string",
  "aggregate_id": "string",
  "occurred_at": "date",
  "event_data": "object",
  "processed": "boolean",
  "created_at": "date"
}
```

### Indexes
- `company_leave_id` (unique)
- `leave_type.code` (unique)
- `is_active`
- `created_at`
- `policy.gender_specific`
- `policy.available_during_probation`

## API Usage Examples

### Create Company Leave

```bash
curl -X POST "http://localhost:8000/api/v1/company-leaves/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "leave_type_code": "CL",
    "leave_type_name": "Casual Leave",
    "leave_category": "casual",
    "annual_allocation": 12,
    "accrual_type": "monthly",
    "description": "Leave for personal reasons",
    "max_carryover_days": 5,
    "min_advance_notice_days": 1,
    "requires_approval": true,
    "auto_approve_threshold": 2,
    "is_encashable": false,
    "available_during_probation": true
  }'
```

### Get All Active Leaves

```bash
curl -X GET "http://localhost:8000/api/v1/company-leaves/active" \
  -H "Authorization: Bearer <token>"
```

### Get Applicable Leaves for Employee

```bash
curl -X GET "http://localhost:8000/api/v1/company-leaves/applicable/employee?employee_gender=female&is_on_probation=false" \
  -H "Authorization: Bearer <token>"
```

### Search Leaves

```bash
curl -X GET "http://localhost:8000/api/v1/company-leaves/search?category=sick&is_encashable=true" \
  -H "Authorization: Bearer <token>"
```

## Testing

### Running Tests

```bash
# Navigate to backend directory
cd backend/app

# Run the test suite
python test_company_leave_implementation.py
```

### Test Coverage

The test suite covers:
- ✅ Creating different leave types (Casual, Sick, Annual, Maternity)
- ✅ Retrieving all and active leaves
- ✅ Employee-specific leave applicability
- ✅ Statistics generation
- ✅ Search functionality
- ✅ Business rule validation
- ✅ Event publishing
- ✅ MongoDB persistence

## Error Handling

### Custom Exceptions

- `CompanyLeaveDTOValidationError` - DTO validation failures
- `CompanyLeaveAlreadyExistsError` - Duplicate leave type codes
- `CompanyLeaveNotFoundError` - Leave not found
- `CreateCompanyLeaveUseCaseError` - Use case execution errors

### HTTP Status Codes

- `201 Created` - Successful creation
- `200 OK` - Successful retrieval
- `400 Bad Request` - Validation errors
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resources
- `500 Internal Server Error` - System errors

## Security

### Authentication & Authorization

- JWT token-based authentication
- Role-based access control (RBAC)
- Hostname-based multi-tenancy
- Input validation and sanitization

### Roles & Permissions

- **superadmin**: Full access to all operations
- **admin**: Create, update, view company leaves
- **manager**: View leaves and statistics
- **user**: View applicable leaves only

## Performance Considerations

### Database Optimization

- Strategic indexing for common queries
- Aggregation pipelines for analytics
- Connection pooling and reuse
- Query optimization for large datasets

### Caching Strategy

- In-memory caching for frequently accessed data
- Redis integration for distributed caching
- Cache invalidation on policy updates

### Scalability

- Horizontal scaling with MongoDB sharding
- Microservice architecture ready
- Event-driven architecture for loose coupling
- Async processing for heavy operations

## Monitoring & Logging

### Structured Logging

- Operation tracking with correlation IDs
- Error logging with stack traces
- Performance metrics and timing
- Business event logging

### Health Checks

- Database connectivity checks
- Service dependency monitoring
- Performance threshold alerts

## Future Enhancements

### Planned Features

1. **Employee Leave Balances**: Individual employee leave tracking
2. **Leave Applications**: Employee leave request workflow
3. **Approval Workflow**: Multi-level approval processes
4. **Calendar Integration**: Leave calendar and scheduling
5. **Reporting Dashboard**: Advanced analytics and insights
6. **Mobile API**: Mobile app integration
7. **Notification System**: Email/SMS notifications
8. **Audit Trail**: Complete change history tracking

### Technical Improvements

1. **GraphQL API**: Alternative to REST endpoints
2. **Event Sourcing**: Complete event-driven architecture
3. **CQRS**: Command Query Responsibility Segregation
4. **Microservices**: Service decomposition
5. **Container Deployment**: Docker and Kubernetes
6. **CI/CD Pipeline**: Automated testing and deployment

## Conclusion

The Company Leave Management System provides a robust, scalable, and maintainable solution for managing company leave policies. Built on Clean Architecture principles and SOLID design patterns, it offers:

- **Comprehensive Business Logic**: Handles complex leave policy scenarios
- **High Code Quality**: Follows industry best practices
- **Excellent Testability**: Easy unit and integration testing
- **Scalable Architecture**: Ready for enterprise deployment
- **Extensible Design**: Easy to add new features
- **Production Ready**: Complete with error handling, logging, and security

The implementation serves as a foundation for a complete leave management system and demonstrates how to build enterprise-grade applications using modern software engineering practices. 