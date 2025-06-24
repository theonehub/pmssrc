# Monthly Taxation System
## Comprehensive Indian Payroll & Taxation API

A modular FastAPI backend implementing Indian payroll and taxation system following SOLID principles and Clean Architecture.

## 🏗️ Architecture Overview

This system implements a **Clean Architecture** with clear separation of concerns:

```
├── app/
│   ├── api/                    # Presentation Layer
│   │   ├── routes/            # FastAPI routes
│   │   └── controllers/       # HTTP controllers
│   ├── application/           # Application Layer
│   │   ├── dto/              # Data Transfer Objects
│   │   ├── interfaces/       # Repository & Service interfaces
│   │   └── use_cases/        # Business use cases
│   ├── domain/               # Domain Layer
│   │   ├── entities/         # Business entities
│   │   ├── value_objects/    # Value objects
│   │   ├── services/         # Domain services
│   │   └── exceptions/       # Domain exceptions
│   ├── infrastructure/       # Infrastructure Layer
│   │   ├── repositories/     # Data persistence
│   │   ├── services/         # External services
│   │   └── database/         # Database connectors
│   ├── config/               # Configuration
│   └── main.py              # Application entry point
```

## 🎯 Features

### Module 1: Salary Component Configuration
- Define custom salary components (BASIC, HRA, LTA, etc.)
- Support for Fixed, Formula, and Variable value types
- Tax exemption section mapping
- Formula engine with safe evaluation
- Component type classification (Earning/Deduction/Reimbursement)

### Module 2: Employee Salary Assignment
- Assign salary structures to employees
- Support for salary revisions with effective dates
- Historical tracking of salary changes
- Component-wise assignment with overrides

### Module 3: Tax Computation Engine
- Support for both Old and New tax regimes
- Automatic tax slab calculations
- Exemption calculations (HRA, LTA, etc.)
- Deduction calculations (80C, 80D, etc.)
- Standard deduction and rebate calculations
- Monthly TDS projections

### Module 4: Payroll Processing
- Monthly payslip generation
- Net pay calculations
- Tax deduction computations
- Component-wise breakdowns

### Module 5: Reporting & Compliance
- Form 16 generation
- FVU (24Q) file generation
- TDS returns
- Tax summary reports

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB 4.4+
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd monthly_taxation
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**
```bash
python -m app.main
```

The API will be available at:
- API Documentation: http://localhost:8001/api/docs
- Health Check: http://localhost:8001/health
- API Info: http://localhost:8001/api/info

## 📚 API Documentation

### Salary Components

**Create Component**
```http
POST /api/v2/salary-components/
Content-Type: application/json

{
  "code": "BASIC",
  "name": "Basic Salary",
  "component_type": "EARNING",
  "value_type": "FIXED",
  "is_taxable": true,
  "default_value": 50000.00,
  "description": "Basic salary component"
}
```

**List Components**
```http
GET /api/v2/salary-components/?page=1&page_size=50&component_type=EARNING
```

**Formula Validation**
```http
POST /api/v2/salary-components/validate-formula
Content-Type: application/json

{
  "formula": "BASIC * 0.4",
  "component_context": {
    "BASIC": 50000
  }
}
```

### Employee Salary

**Assign Salary Structure**
```http
POST /api/v2/employee-salary/
Content-Type: application/json

{
  "employee_id": "EMP001",
  "employee_code": "EMP001",
  "gross_salary": 100000.00,
  "effective_from": "2024-01-01",
  "components": [
    {
      "component_code": "BASIC",
      "value": 50000.00
    },
    {
      "component_code": "HRA", 
      "formula_override": "BASIC * 0.4"
    }
  ]
}
```

### Tax Computation

**Calculate Tax**
```http
POST /api/v2/tax-computation/
Content-Type: application/json

{
  "employee_id": "EMP001",
  "financial_year": "2023-24",
  "tax_regime": "NEW_REGIME",
  "gross_salary": 1200000.00,
  "other_income": 50000.00,
  "deductions": {
    "80C": 150000.00,
    "80D": 25000.00
  }
}
```

## 🏛️ SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- Each class has a single, well-defined responsibility
- `SalaryComponent` entity only handles component business logic
- `FormulaEngine` only handles formula validation and evaluation
- Controllers only handle HTTP concerns

### Open/Closed Principle (OCP)
- Easy to add new component types without modifying existing code
- New tax regimes can be added by extending interfaces
- Formula engine can support new functions without core changes

### Liskov Substitution Principle (LSP)
- Repository implementations are interchangeable
- Service implementations can be swapped without breaking clients
- Tax regime calculators follow common interfaces

### Interface Segregation Principle (ISP)
- Small, focused interfaces for repositories and services
- Clients depend only on methods they actually use
- Clear separation between read and write operations

### Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions, not concretions
- Dependency injection container manages all dependencies
- Easy to mock dependencies for testing

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_salary_component.py

# Run tests with logging
pytest -s --log-cli-level=INFO
```

### Test Structure
```
tests/
├── unit/                 # Unit tests
│   ├── domain/          # Domain layer tests
│   ├── application/     # Application layer tests
│   └── infrastructure/  # Infrastructure tests
├── integration/         # Integration tests
└── fixtures/           # Test data fixtures
```

## 🐳 Docker Support

### Build and Run
```bash
# Build image
docker build -t monthly-taxation .

# Run container
docker run -p 8001:8001 monthly-taxation

# Docker Compose
docker-compose up -d
```

## 📊 Performance Considerations

### Database Optimization
- Proper indexing on frequently queried fields
- Organization-based data segregation
- Connection pooling for high concurrency

### Caching Strategy
- Redis for frequently accessed component configurations
- In-memory caching for tax slabs and rates
- API response caching for static data

### Monitoring
- Structured logging with correlation IDs
- Metrics collection for API performance
- Health checks for all dependencies

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Organization-level data isolation

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- Audit logging for all changes

## 🚀 Deployment

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring and logging configured
- [ ] Backup strategy implemented
- [ ] Load balancer configured

### Environment Configuration
```bash
# Production environment
export ENVIRONMENT=production
export DATABASE_URL=mongodb://prod-cluster
export LOG_LEVEL=INFO
export CORS_ORIGINS=https://yourdomain.com
```

## 📈 Roadmap

### Phase 1 - Core Features ✅
- Salary component management
- Employee salary assignment
- Basic tax computation

### Phase 2 - Advanced Features 🚧
- Form 16 generation
- FVU file generation
- Investment declaration module

### Phase 3 - Enterprise Features 📋
- Multi-company support
- Advanced reporting
- API rate limiting
- Audit trails

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Add type hints for all functions
- Write comprehensive docstrings

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation at `/api/docs`
- Review the architecture guide in `docs/`

---

**Built with ❤️ using FastAPI, MongoDB, and Clean Architecture principles** 