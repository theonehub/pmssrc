#!/bin/bash

# PMS Microservices Setup Script
# This script sets up the development environment for the microservices project

set -e

echo "🚀 Setting up PMS Microservices Development Environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✅"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_status "Python $python_version is installed ✅"
}

# Create necessary directories
create_directories() {
    print_status "Creating project directories..."
    
    directories=(
        "uploads"
        "logs"
        "data/mongodb"
        "data/redis"
        "data/rabbitmq"
        "infrastructure/mongo-init"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_status "Created directory: $dir"
    done
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    cat > .env << EOF
# PMS Microservices Environment Configuration

# MongoDB Configuration
MONGODB_URL=mongodb://admin:password123@mongodb:27017/
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password123

# Redis Configuration
REDIS_URL=redis://redis:6379

# RabbitMQ Configuration
RABBITMQ_URL=amqp://admin:password123@rabbitmq:5672/
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=password123

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Service URLs (for inter-service communication)
USER_SERVICE_URL=http://user-service:8000
ORGANIZATION_SERVICE_URL=http://organization-service:8000
LEAVE_SERVICE_URL=http://leave-service:8000
ATTENDANCE_SERVICE_URL=http://attendance-service:8000
REIMBURSEMENT_SERVICE_URL=http://reimbursement-service:8000
PROJECT_SERVICE_URL=http://project-service:8000
PAYROLL_SERVICE_URL=http://payroll-service:8000
TAXATION_SERVICE_URL=http://taxation-service:8000
REPORTING_SERVICE_URL=http://reporting-service:8000

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000

# Development/Production Mode
ENVIRONMENT=development
DEBUG=true
EOF

    print_status "Created .env file with default configuration"
    print_warning "Please review and update the .env file with your specific settings"
}

# Create MongoDB initialization script
create_mongo_init() {
    print_status "Creating MongoDB initialization script..."
    
    cat > infrastructure/mongo-init/init.js << 'EOF'
// MongoDB Initialization Script for PMS Microservices

// Create admin user
db = db.getSiblingDB('admin');
db.createUser({
    user: 'admin',
    pwd: 'password123',
    roles: [
        { role: 'userAdminAnyDatabase', db: 'admin' },
        { role: 'readWriteAnyDatabase', db: 'admin' },
        { role: 'dbAdminAnyDatabase', db: 'admin' }
    ]
});

// Function to create service databases
function createServiceDatabase(serviceName) {
    const dbName = serviceName + '_default';
    const serviceDb = db.getSiblingDB(dbName);
    
    // Create a dummy collection to initialize the database
    serviceDb.init.insertOne({ initialized: new Date() });
    
    print('Created database: ' + dbName);
}

// Create databases for each microservice
const services = [
    'user_service',
    'organization_service', 
    'leave_service',
    'attendance_service',
    'reimbursement_service',
    'project_service',
    'payroll_service',
    'taxation_service',
    'reporting_service'
];

services.forEach(createServiceDatabase);

print('MongoDB initialization completed for PMS Microservices');
EOF

    print_status "Created MongoDB initialization script"
}

# Setup development tools
setup_dev_tools() {
    print_status "Setting up development tools..."
    
    # Create pre-commit hooks
    cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
EOF

    # Create gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Environment variables
.env
.env.local
.env.production

# Docker
docker-compose.override.yml

# Database
data/

# Uploads
uploads/

# Temporary files
tmp/
temp/
EOF

    print_status "Created development configuration files"
}

# Create helpful scripts
create_scripts() {
    print_status "Creating helper scripts..."
    
    # Start script
    cat > scripts/start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting PMS Microservices..."
docker-compose up -d
echo "✅ Services started. Access the API Gateway at http://localhost:8000"
echo "📊 RabbitMQ Management: http://localhost:15672 (admin/password123)"
EOF

    # Stop script
    cat > scripts/stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping PMS Microservices..."
docker-compose down
echo "✅ All services stopped"
EOF

    # Logs script
    cat > scripts/logs.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./scripts/logs.sh <service-name>"
    echo "Available services: user-service, organization-service, leave-service, etc."
    exit 1
fi
docker-compose logs -f "$1"
EOF

    # Build script
    cat > scripts/build.sh << 'EOF'
#!/bin/bash
echo "🔨 Building all microservices..."
docker-compose build
echo "✅ Build completed"
EOF

    # Migration script
    cat > scripts/migrate.sh << 'EOF'
#!/bin/bash
echo "🔄 Running migration from monolith..."
python3 scripts/migrate_from_monolith.py --all
echo "✅ Migration completed"
EOF

    # Make scripts executable
    chmod +x scripts/*.sh
    
    print_status "Created helper scripts in scripts/ directory"
}

# Display final instructions
show_instructions() {
    echo ""
    echo -e "${BLUE}🎉 PMS Microservices setup completed!${NC}"
    echo ""
    echo -e "${GREEN}Next Steps:${NC}"
    echo "1. Review and update the .env file with your configuration"
    echo "2. If migrating from monolith, run: ./scripts/migrate.sh"
    echo "3. Start the services: ./scripts/start.sh"
    echo "4. Access the API Gateway at http://localhost:8000"
    echo ""
    echo -e "${GREEN}Available Commands:${NC}"
    echo "• ./scripts/start.sh    - Start all services"
    echo "• ./scripts/stop.sh     - Stop all services"
    echo "• ./scripts/build.sh    - Build all services"
    echo "• ./scripts/logs.sh <service> - View service logs"
    echo "• ./scripts/migrate.sh  - Migrate from monolith"
    echo ""
    echo -e "${GREEN}Service Ports:${NC}"
    echo "• API Gateway:      http://localhost:8000"
    echo "• User Service:     http://localhost:8001"
    echo "• Organization:     http://localhost:8002"
    echo "• Leave Service:    http://localhost:8003"
    echo "• Attendance:       http://localhost:8004"
    echo "• Reimbursement:    http://localhost:8005"
    echo "• Project Service:  http://localhost:8006"
    echo "• Payroll Service:  http://localhost:8007"
    echo "• Taxation Service: http://localhost:8008"
    echo "• Reporting:        http://localhost:8009"
    echo ""
    echo -e "${GREEN}Management UIs:${NC}"
    echo "• RabbitMQ:         http://localhost:15672"
    echo "• MongoDB:          localhost:27017"
    echo ""
}

# Main execution
main() {
    print_status "Starting PMS Microservices setup..."
    
    check_docker
    check_python
    create_directories
    create_env_file
    create_mongo_init
    setup_dev_tools
    create_scripts
    show_instructions
    
    print_status "Setup completed successfully! 🎉"
}

# Run main function
main "$@" 