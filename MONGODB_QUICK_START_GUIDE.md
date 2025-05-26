# MongoDB Taxation System - Quick Start Guide

This guide will help you quickly set up the MongoDB-based taxation system from scratch.

## Prerequisites

- Python 3.8+
- MongoDB 4.4+ (local or remote)
- Git

## Step 1: Environment Setup

### 1.1 Install MongoDB (if running locally)

```bash
# macOS (using Homebrew)
brew tap mongodb/brew
brew install mongodb-community

# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 1.2 Install Python Dependencies

```bash
# Navigate to backend directory
cd backend

# Install required packages
pip install pymongo motor fastapi uvicorn pydantic python-jose passlib bcrypt
```

### 1.3 Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# .env file
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=pms_taxation
MONGODB_MAX_POOL_SIZE=100
MONGODB_MIN_POOL_SIZE=10
MONGODB_CONNECT_TIMEOUT_MS=10000
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000

# Optional authentication (leave empty for local development)
MONGODB_USERNAME=
MONGODB_PASSWORD=
MONGODB_AUTH_SOURCE=admin

# Optional SSL (set to false for local development)
MONGODB_USE_SSL=false
```

## Step 2: Database Initialization

### 2.1 Run the MongoDB Initialization Script

```bash
# From the backend/app directory
cd app
python scripts/init_mongodb.py
```

This script will:
- Create all required collections
- Set up validation schemas
- Create performance indexes
- Verify the setup

### 2.2 Verify Database Setup

```bash
# Test MongoDB connection
python -c "
from config.mongodb_config import get_database_config
from database.mongodb_taxation_database import MongoDBTaxationDatabase

config = get_database_config()
db = MongoDBTaxationDatabase(config['connection_string'], config['database_name'])
print('✅ MongoDB connection successful')
print(f'Database: {config[\"database_name\"]}')
db.close_connection()
"
```

## Step 3: Initialize Services

### 3.1 Test the Enhanced Taxation Service

```python
# test_services.py
from services.enhanced_taxation_service import EnhancedTaxationService
from database.mongodb_taxation_database import MongoDBTaxationDatabase
from config.mongodb_config import get_database_config

# Initialize database
config = get_database_config()
db_service = MongoDBTaxationDatabase(config['connection_string'], config['database_name'])

# Initialize taxation service
tax_service = EnhancedTaxationService(db_service)

# Test basic functionality
print("✅ Enhanced Taxation Service initialized successfully")
```

### 3.2 Test Tax Calculation

```python
# test_calculation.py
from strategies.tax_calculation_strategies import TaxCalculationEngine, TaxCalculationContext
from datetime import datetime

# Create test context
context = TaxCalculationContext(
    employee_id="TEST001",
    tax_year="2024-25",
    calculation_date=datetime.now(),
    regime="new",
    age=30,
    is_govt_employee=False,
    gross_income=1200000,
    basic_salary=600000,
    hra=240000,
    special_allowance=360000,
    deductions={
        "section_80c": 150000,
        "section_80d": 25000
    }
)

# Calculate tax
engine = TaxCalculationEngine()
result = engine.calculate_tax(context)

print(f"✅ Tax calculation successful")
print(f"Total Tax: ₹{result.total_tax:,.2f}")
print(f"Effective Tax Rate: {result.effective_tax_rate:.2f}%")
```

## Step 4: API Setup (Optional)

### 4.1 Create FastAPI Application

```python
# main.py
from fastapi import FastAPI, Depends
from services.enhanced_taxation_service import EnhancedTaxationService
from database.mongodb_taxation_database import MongoDBTaxationDatabase
from config.mongodb_config import get_database_config

app = FastAPI(title="Taxation System API")

# Initialize services
config = get_database_config()
db_service = MongoDBTaxationDatabase(config['connection_string'], config['database_name'])
tax_service = EnhancedTaxationService(db_service)

@app.get("/")
async def root():
    return {"message": "Taxation System API is running"}

@app.post("/calculate-tax/{employee_id}")
async def calculate_tax(employee_id: str):
    try:
        result = tax_service.calculate_employee_tax(employee_id)
        return {"status": "success", "data": result.to_dict()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4.2 Run the API

```bash
# Start the API server
python main.py

# Test the API
curl http://localhost:8000/
```

## Step 5: Create Test Data (Optional)

### 5.1 Create Sample Employee Data

```python
# scripts/create_sample_data.py
from database.mongodb_taxation_database import MongoDBTaxationDatabase
from config.mongodb_config import get_database_config
from models.taxation import Taxation, SalaryComponents
from datetime import datetime

def create_sample_data():
    config = get_database_config()
    db = MongoDBTaxationDatabase(config['connection_string'], config['database_name'])
    
    # Sample employees
    employees = [
        {
            "emp_id": "EMP001",
            "hostname": "company.com",
            "emp_age": 28,
            "regime": "new",
            "basic": 50000,
            "hra": 20000,
            "special_allowance": 15000
        },
        {
            "emp_id": "EMP002",
            "hostname": "company.com", 
            "emp_age": 35,
            "regime": "old",
            "basic": 75000,
            "hra": 30000,
            "special_allowance": 25000
        }
    ]
    
    for emp in employees:
        taxation_data = {
            "emp_id": emp["emp_id"],
            "emp_age": emp["emp_age"],
            "regime": emp["regime"],
            "tax_year": "2024-2025",
            "basic": emp["basic"],
            "hra": emp["hra"],
            "special_allowance": emp["special_allowance"],
            "total_tax": 0,
            "filing_status": "draft",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        db.save_taxation(taxation_data, emp["hostname"])
        print(f"✅ Created sample data for {emp['emp_id']}")
    
    db.close_connection()

if __name__ == "__main__":
    create_sample_data()
```

## Step 6: Verification

### 6.1 Check Database Collections

```bash
# Connect to MongoDB shell
mongo

# Switch to taxation database
use pms_taxation

# List collections
show collections

# Check sample data
db.taxation.find().pretty()
db.tax_events.find().pretty()
```

### 6.2 Run System Tests

```python
# test_system.py
from services.enhanced_taxation_service import EnhancedTaxationService
from database.mongodb_taxation_database import MongoDBTaxationDatabase
from config.mongodb_config import get_database_config

def test_complete_system():
    # Initialize services
    config = get_database_config()
    db_service = MongoDBTaxationDatabase(config['connection_string'], config['database_name'])
    tax_service = EnhancedTaxationService(db_service)
    
    # Test tax calculation
    try:
        result = tax_service.calculate_employee_tax("EMP001")
        print(f"✅ Tax calculation successful: ₹{result.total_tax:,.2f}")
    except Exception as e:
        print(f"❌ Tax calculation failed: {e}")
    
    # Test event processing
    try:
        events = tax_service.process_pending_events()
        print(f"✅ Event processing successful: {len(events)} events processed")
    except Exception as e:
        print(f"❌ Event processing failed: {e}")
    
    # Test regime comparison
    try:
        comparison = tax_service.compare_tax_regimes("EMP001")
        print(f"✅ Regime comparison successful")
    except Exception as e:
        print(f"❌ Regime comparison failed: {e}")
    
    db_service.close_connection()

if __name__ == "__main__":
    test_complete_system()
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   ```bash
   # Check if MongoDB is running
   sudo systemctl status mongod
   
   # Check MongoDB logs
   sudo tail -f /var/log/mongodb/mongod.log
   ```

2. **Import Errors**
   ```bash
   # Make sure you're in the correct directory
   cd backend/app
   
   # Add current directory to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. **Permission Errors**
   ```bash
   # Check MongoDB data directory permissions
   sudo chown -R mongodb:mongodb /var/lib/mongodb
   sudo chown mongodb:mongodb /tmp/mongodb-27017.sock
   ```

4. **Collection Creation Failed**
   ```bash
   # Check MongoDB version compatibility
   mongo --version
   
   # Ensure user has proper permissions
   # Connect to MongoDB and create user if needed
   ```

## Next Steps

1. **Explore the API**: Use the FastAPI automatic documentation at `http://localhost:8000/docs`
2. **Add More Test Data**: Create additional employee records for testing
3. **Implement Frontend**: Connect the React frontend to the new API
4. **Set up Monitoring**: Implement logging and metrics collection
5. **Production Deployment**: Follow the production deployment guide

## Support

For issues or questions:
1. Check the main implementation guide: `TAXATION_SYSTEM_IMPLEMENTATION_GUIDE.md`
2. Review the architecture documentation: `TAXATION_SYSTEM_REARCHITECTURE_PROPOSAL.md`
3. Examine the comprehensive scenarios: `TAX_COMPUTATION_SCENARIOS_COMPREHENSIVE.md`

---

**Congratulations!** 🎉 You now have a fully functional MongoDB-based taxation system with event-driven architecture and comprehensive tax calculation capabilities. 