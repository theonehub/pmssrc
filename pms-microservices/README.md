# Personnel Management System - Microservices Architecture

A modern microservices-based Personnel Management System built with FastAPI, MongoDB, and Docker.

## 🏗️ Architecture Overview

This project decomposes the monolithic PMS into independent microservices, each handling a specific business domain:

```
pms-microservices/
├── services/                    # Individual microservices
│   ├── user-service/           # Authentication & user management
│   ├── organization-service/   # Multi-tenant organization data
│   ├── leave-service/          # Leave management & policies
│   ├── attendance-service/     # Time tracking & attendance
│   ├── reimbursement-service/  # Expense claims & approvals
│   ├── project-service/        # Project attributes & configs
│   ├── payroll-service/        # Salary calculations & payslips
│   ├── taxation-service/       # Tax calculations & compliance
│   └── reporting-service/      # Analytics & cross-service reports
├── shared/                     # Shared libraries & utilities
├── infrastructure/             # Infrastructure as code
├── scripts/                    # Migration & deployment scripts
└── docs/                      # Architecture documentation
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- MongoDB (via Docker)

### 1. Clone and Setup
```bash
git clone <your-repo>
cd pms-microservices
```

### 2. Start Infrastructure
```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
docker-compose up user-service organization-service
```

### 3. Access Services
- **API Gateway**: http://localhost:8000
- **User Service**: http://localhost:8001
- **Organization Service**: http://localhost:8002
- **Leave Service**: http://localhost:8003
- **Frontend**: http://localhost:3000

## 🏛️ Service Architecture

### Core Services (Phase 1)
- **User Service** (Port 8001): Authentication, JWT, user profiles
- **Organization Service** (Port 8002): Multi-tenancy, company settings

### Business Services (Phase 2)  
- **Leave Service** (Port 8003): Leave requests, policies, holidays
- **Attendance Service** (Port 8004): Time tracking, schedules
- **Reimbursement Service** (Port 8005): Expense claims, receipts
- **Project Service** (Port 8006): Project attributes, configurations

### Complex Services (Phase 3)
- **Payroll Service** (Port 8007): Salary calculations, payslips
- **Taxation Service** (Port 8008): Tax calculations, compliance

### Analytics Services (Phase 4)
- **Reporting Service** (Port 8009): Cross-service analytics, dashboards

## 🗄️ Database Strategy

Each service has its own MongoDB database:
```
user_service_{hostname}
organization_service_{hostname}
leave_service_{hostname}
attendance_service_{hostname}
reimbursement_service_{hostname}
project_service_{hostname}
payroll_service_{hostname}
taxation_service_{hostname}
reporting_service_{hostname}
```

## 🔧 Development

### Running Individual Services
```bash
cd services/user-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Building Docker Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build user-service
```

### Migration from Monolith
```bash
# Run migration scripts
python scripts/migrate_data.py --service user-service
python scripts/migrate_data.py --service organization-service
```

## 🌐 API Gateway

All external requests go through Kong API Gateway:
```
http://localhost:8000/api/v2/auth/*     -> User Service
http://localhost:8000/api/v2/users/*    -> User Service
http://localhost:8000/api/v2/organizations/* -> Organization Service
http://localhost:8000/api/v2/leaves/*   -> Leave Service
http://localhost:8000/api/v2/attendance/* -> Attendance Service
# ... etc
```

## 📊 Monitoring & Observability

- **Health Checks**: Each service exposes `/health` endpoint
- **Metrics**: Prometheus metrics at `/metrics`
- **Logging**: Structured JSON logs
- **Tracing**: Distributed tracing with correlation IDs

## 🔐 Security

- **JWT Authentication**: Centralized through User Service
- **API Gateway**: Rate limiting, CORS, request validation
- **Service-to-Service**: Internal JWT tokens
- **Database**: Per-service MongoDB instances

## 🚀 Deployment

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes (Future)
```bash
kubectl apply -f k8s/
```

## 📈 Migration Timeline

### Phase 1: Foundation (Weeks 1-2)
- ✅ User Service
- ✅ Organization Service  
- ✅ API Gateway setup

### Phase 2: Business Logic (Weeks 3-4)
- ✅ Leave Service
- ✅ Attendance Service
- ✅ Reimbursement Service
- ✅ Project Service

### Phase 3: Complex Services (Weeks 5-6)
- ✅ Payroll Service
- ✅ Taxation Service

### Phase 4: Analytics (Week 7)
- ✅ Reporting Service

## 🤝 Contributing

1. Choose a service to work on
2. Follow the service template structure
3. Ensure all tests pass
4. Update API documentation
5. Submit pull request

## 📚 Documentation

- [Service Development Guide](docs/service-development.md)
- [API Documentation](docs/api-reference.md)
- [Deployment Guide](docs/deployment.md)
- [Migration Guide](docs/migration-guide.md)

## 🔍 Troubleshooting

### Common Issues
- **Port conflicts**: Check if ports 8000-8009 are available
- **Database connection**: Ensure MongoDB is running
- **Service discovery**: Verify Docker network connectivity

### Logs
```bash
# View service logs
docker-compose logs user-service
docker-compose logs -f --tail=100 user-service
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 