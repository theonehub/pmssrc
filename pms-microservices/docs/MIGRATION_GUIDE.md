# PMS Monolith to Microservices Migration Guide

This guide provides step-by-step instructions for migrating your Personnel Management System from a monolithic architecture to microservices.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Migration Strategy](#migration-strategy)
3. [Step-by-Step Migration](#step-by-step-migration)
4. [Service Architecture](#service-architecture)
5. [Database Migration](#database-migration)
6. [Frontend Adaptation](#frontend-adaptation)
7. [Testing Strategy](#testing-strategy)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Technical Requirements
- **Docker & Docker Compose**: For containerization
- **Python 3.11+**: For service development
- **MongoDB**: Database (will be containerized)
- **Node.js 16+**: For frontend (if included)
- **Git**: Version control

### Knowledge Requirements
- Understanding of microservices architecture
- Familiarity with FastAPI and MongoDB
- Basic Docker knowledge
- Understanding of your current monolithic codebase

## 🎯 Migration Strategy

### Phase-Based Approach

We'll migrate services in phases based on complexity and dependencies:

#### Phase 1: Foundation Services (Week 1-2)
✅ **Core Services** - Services other services depend on
- **User Service**: Authentication, user profiles, permissions
- **Organization Service**: Multi-tenancy, company settings

#### Phase 2: Business Logic Services (Week 3-4)
✅ **Independent Business Services**
- **Leave Service**: Leave requests, policies, holidays
- **Attendance Service**: Time tracking, schedules
- **Reimbursement Service**: Expense claims, receipts
- **Project Service**: Project attributes, configurations

#### Phase 3: Complex Services (Week 5-6)
✅ **Services with Heavy Business Logic**
- **Payroll Service**: Salary calculations, payslips
- **Taxation Service**: Tax calculations, compliance

#### Phase 4: Analytics Services (Week 7)
✅ **Cross-Cutting Services**
- **Reporting Service**: Analytics, dashboards

## 🚀 Step-by-Step Migration

### Step 1: Environment Setup

```bash
# 1. Clone the microservices project
git clone <your-microservices-repo>
cd pms-microservices

# 2. Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Review the .env file
vi .env  # Update with your specific settings
```

### Step 2: Database Migration Planning

Before migrating, understand your current database structure:

```bash
# Connect to your monolith MongoDB
mongo your-monolith-db

# List all collections
show collections

# Analyze data distribution
db.users.countDocuments()
db.employee_leaves.countDocuments()
# ... etc for all collections
```

### Step 3: Service-by-Service Migration

#### 3.1 User Service Migration

```bash
# Start with User Service (foundation service)
python3 scripts/migrate_from_monolith.py --service user-service

# Review migrated code
cd services/user-service
ls -la

# Update imports and dependencies
# Check main.py, routes, use cases, repositories
```

**Manual Adjustments Needed:**
- Update import statements
- Fix dependency injection
- Update database connections
- Test authentication flow

#### 3.2 Organization Service Migration

```bash
python3 scripts/migrate_from_monolith.py --service organization-service
```

**Key Points:**
- Ensure hostname-based database selection works
- Test multi-tenancy functionality
- Verify organization settings migration

#### 3.3 Continue with Other Services

Repeat the process for each service in order:

```bash
# Phase 2 Services
python3 scripts/migrate_from_monolith.py --service leave-service
python3 scripts/migrate_from_monolith.py --service attendance-service
python3 scripts/migrate_from_monolith.py --service reimbursement-service
python3 scripts/migrate_from_monolith.py --service project-service

# Phase 3 Services  
python3 scripts/migrate_from_monolith.py --service payroll-service
python3 scripts/migrate_from_monolith.py --service taxation-service

# Phase 4 Services
python3 scripts/migrate_from_monolith.py --service reporting-service
```

### Step 4: Service Communication Setup

#### 4.1 Update Inter-Service Communication

Services that previously accessed data directly now need HTTP calls:

```python
# Before (Monolith)
user = user_repository.get_by_id(employee_id)

# After (Microservices)
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(
        f"{USER_SERVICE_URL}/api/v2/users/{employee_id}",
        headers=await get_service_headers("leave_service")
    )
    user = response.json()
```

#### 4.2 Implement Event-Driven Communication

For critical operations, use events:

```python
# Example: User creation event
from shared.events import EventPublisher

async def create_user(user_data):
    # Create user in User Service
    user = await user_repository.create(user_data)
    
    # Publish event for other services
    await EventPublisher.publish("user.created", {
        "employee_id": user.employee_id,
        "email": user.email,
        "organization_id": user.organization_id
    })
```

### Step 5: Database Migration

#### 5.1 Backup Current Database

```bash
# Create full backup
mongodump --uri="mongodb://your-monolith-connection" --out=backup/

# Create backup per service
mongodump --uri="mongodb://your-monolith-connection" --collection=users --out=backup/users/
```

#### 5.2 Run Data Migration

```bash
# Migrate all service data
python3 scripts/migrate_from_monolith.py --all

# Or migrate specific service data
python3 scripts/migrate_from_monolith.py --service user-service
```

#### 5.3 Verify Data Migration

```bash
# Connect to new databases
mongo "mongodb://admin:password123@localhost:27017/user_service_default"

# Verify data
db.users.countDocuments()
db.users.findOne()

# Compare with original
mongo "mongodb://your-monolith-connection/original_db"
db.users.countDocuments()
```

### Step 6: API Gateway Configuration

The Kong API Gateway routes requests to appropriate services:

```yaml
# Update infrastructure/kong/kong.yml
routes:
  - name: user-routes
    service: user-service
    paths:
      - /api/v2/users
      - /api/v2/auth
```

### Step 7: Frontend Updates

#### 7.1 Update API Base URLs

```javascript
// Before (Monolith)
const API_BASE = 'http://localhost:8000';

// After (Microservices - via API Gateway)
const API_BASE = 'http://localhost:8000';  // Same, but routed by Gateway
```

#### 7.2 Update Authentication

```javascript
// Frontend auth service remains mostly the same
// API Gateway handles routing to User Service
const login = async (credentials) => {
  const response = await fetch(`${API_BASE}/api/v2/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  return response.json();
};
```

## 🏗️ Service Architecture Details

### Service Structure

Each service follows clean architecture:

```
service-name/
├── domain/
│   ├── entities/           # Business entities
│   ├── value_objects/      # Value objects
│   └── events/            # Domain events
├── application/
│   ├── use_cases/         # Business logic
│   ├── dto/               # Data transfer objects
│   └── interfaces/        # Repository interfaces
├── infrastructure/
│   ├── repositories/      # Database access
│   ├── services/          # External services
│   └── database/          # DB configuration
├── api/
│   ├── routes/            # FastAPI routes
│   └── controllers/       # Request handlers
├── main.py               # Service entry point
├── Dockerfile            # Container definition
└── requirements.txt      # Dependencies
```

### Database Per Service

Each service has its own database:

```
MongoDB Cluster:
├── user_service_{hostname}
├── organization_service_{hostname}
├── leave_service_{hostname}
├── attendance_service_{hostname}
├── reimbursement_service_{hostname}
├── project_service_{hostname}
├── payroll_service_{hostname}
├── taxation_service_{hostname}
└── reporting_service_{hostname}
```

## 🧪 Testing Strategy

### 1. Unit Testing

Test each service independently:

```python
# Example: User Service unit test
import pytest
from application.use_cases.create_user_use_case import CreateUserUseCase

@pytest.mark.asyncio
async def test_create_user():
    use_case = CreateUserUseCase(mock_user_repository)
    result = await use_case.execute(user_data)
    assert result.employee_id is not None
```

### 2. Integration Testing

Test service interactions:

```python
# Example: Leave Service integration test
@pytest.mark.asyncio 
async def test_leave_approval():
    # Mock User Service response
    with aioresponses() as m:
        m.get(f"{USER_SERVICE_URL}/api/v2/users/123", payload=user_data)
        
        result = await leave_use_case.approve_leave(leave_id, approver_id)
        assert result.status == "approved"
```

### 3. End-to-End Testing

Test complete workflows:

```python
# Example: Full leave request workflow
async def test_leave_request_workflow():
    # 1. Create user
    user = await create_test_user()
    
    # 2. Apply for leave
    leave = await apply_for_leave(user.employee_id, leave_data)
    
    # 3. Approve leave
    approved = await approve_leave(leave.id, manager_id)
    
    # 4. Verify attendance impact
    attendance = await get_attendance_summary(user.employee_id, date_range)
    
    assert approved.status == "approved"
    assert attendance.leave_days_taken > 0
```

## 🚀 Deployment

### Development Deployment

```bash
# Start all services
./scripts/start.sh

# View logs
./scripts/logs.sh user-service

# Stop services
./scripts/stop.sh
```

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production settings
docker-compose -f docker-compose.prod.yml up -d

# Scale services based on load
docker-compose -f docker-compose.prod.yml up -d --scale user-service=3
```

### Kubernetes Deployment (Future)

```yaml
# k8s/user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: pms/user-service:latest
        ports:
        - containerPort: 8000
```

## 🔍 Monitoring & Observability

### Health Checks

Each service exposes health endpoints:

```bash
# Check service health
curl http://localhost:8001/health  # User Service
curl http://localhost:8002/health  # Organization Service
```

### Centralized Logging

Services use structured logging:

```python
import structlog

logger = structlog.get_logger()

logger.info("User created", 
    employee_id=user.employee_id,
    service="user_service",
    action="create_user"
)
```

### Metrics Collection

```python
# Prometheus metrics example
from prometheus_client import Counter, Histogram

user_creation_counter = Counter('users_created_total', 'Total users created')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@request_duration.time()
async def create_user(user_data):
    result = await use_case.execute(user_data)
    user_creation_counter.inc()
    return result
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Service Communication Errors

**Problem**: Services can't communicate with each other

**Solution**:
```bash
# Check Docker network
docker network ls
docker network inspect pms-network

# Verify service URLs
docker-compose logs user-service | grep "USER_SERVICE_URL"
```

#### 2. Database Connection Issues

**Problem**: Services can't connect to MongoDB

**Solution**:
```bash
# Check MongoDB status
docker-compose logs mongodb

# Test connection
docker exec -it pms-mongodb mongo -u admin -p password123
```

#### 3. Authentication Issues

**Problem**: JWT tokens not working across services

**Solution**:
```bash
# Verify JWT secret consistency
grep JWT_SECRET .env
docker-compose logs user-service | grep JWT
```

#### 4. Data Migration Issues

**Problem**: Data not migrating correctly

**Solution**:
```bash
# Check migration logs
python3 scripts/migrate_from_monolith.py --service user-service --verbose

# Verify data manually
mongo "mongodb://admin:password123@localhost:27017/user_service_default"
db.users.find().limit(5)
```

### Performance Issues

#### 1. Slow Service Responses

**Diagnosis**:
```bash
# Check service metrics
curl http://localhost:8001/metrics

# Monitor resource usage
docker stats
```

**Solutions**:
- Add database indexes
- Implement caching with Redis
- Optimize database queries
- Scale horizontally

#### 2. High Memory Usage

**Diagnosis**:
```bash
# Check memory usage per service
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**Solutions**:
- Optimize data structures
- Implement connection pooling
- Add memory limits in docker-compose.yml

## 📚 Additional Resources

### Documentation
- [Service Development Guide](SERVICE_DEVELOPMENT.md)
- [API Reference](API_REFERENCE.md) 
- [Deployment Guide](DEPLOYMENT.md)

### External Resources
- [Microservices Patterns](https://microservices.io/patterns/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Best Practices](https://docs.mongodb.com/manual/administration/production-notes/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## 🎯 Success Criteria

Your migration is successful when:

✅ All services start without errors
✅ API Gateway routes requests correctly  
✅ Authentication works across services
✅ Database operations succeed
✅ Frontend functions normally
✅ Inter-service communication works
✅ Performance is acceptable
✅ Monitoring and logging are functional

## 📞 Support

If you encounter issues during migration:

1. Check the troubleshooting section above
2. Review service logs: `./scripts/logs.sh <service-name>`
3. Verify configuration in `.env` file
4. Test services individually before testing together
5. Compare with working service examples

Good luck with your migration! 🚀 