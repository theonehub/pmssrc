# Enhanced Project Attributes Implementation

## 📋 **Overview**

The Project Attributes module has been significantly enhanced to support organization-specific configurations with multiple value types. This implementation allows organizations to define custom configuration attributes that can be used throughout the application for feature flags, settings, and configuration values.

## 🎯 **Key Features**

### **1. Multiple Value Types**
- **Boolean**: True/false values (e.g., `monthly_disburse_lta`)
- **String**: Short text values
- **Number**: Numeric values with min/max validation
- **Text**: Longer text values
- **Multiline Text**: Multi-line text (e.g., addresses)
- **Dropdown**: Selection from predefined options
- **Email**: Email addresses with validation
- **Phone**: Phone numbers with format validation
- **URL**: Web URLs
- **Date**: Date values in ISO format
- **JSON**: JSON data structures

### **2. Organization-Specific Configuration**
- Multi-tenant support via hostname-based organization isolation
- Organization-specific attribute keys and values
- Default values for each organization
- Category-based grouping

### **3. Validation & Business Rules**
- Type-specific validation rules
- Key format validation (alphanumeric, underscores, hyphens)
- Length constraints for descriptions and categories
- Dropdown option validation
- Numeric range validation

### **4. System vs Custom Attributes**
- System-managed attributes (predefined templates)
- Custom attributes (user-defined)
- Different permission levels for system vs custom attributes

## 🏗️ **Architecture**

### **Clean Architecture Layers**

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│  Routes → Controllers → Use Cases → Services → Repositories │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                             │
├─────────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                        │
└─────────────────────────────────────────────────────────────┘
```

### **Key Components**

1. **Domain Entity**: `ProjectAttribute` - Core business object
2. **DTOs**: Enhanced data transfer objects with type support
3. **Use Cases**: Business logic for CRUD operations
4. **Repository**: MongoDB-based data persistence
5. **Controller**: HTTP request handling
6. **Routes**: RESTful API endpoints

## 📊 **Data Model**

### **Enhanced DTOs**

```python
class ProjectAttributeCreateRequestDTO(BaseModel):
    key: str                    # Unique identifier
    value: Union[str, bool, int, float]  # Typed value
    value_type: ValueType       # Type classification
    description: Optional[str]  # Description
    is_active: bool = True      # Active status
    default_value: Optional[Union[str, bool, int, float]]  # Default
    validation_rules: Optional[Dict[str, Any]]  # Type-specific rules
    category: Optional[str]     # Category grouping
    is_system: bool = False     # System-managed flag
```

### **Domain Entity**

```python
class ProjectAttribute(BaseEntity):
    key: str
    value: Union[str, bool, int, float]
    value_type: ValueType
    organisation_id: OrganisationId
    description: Optional[str]
    is_active: bool
    default_value: Optional[Union[str, bool, int, float]]
    validation_rules: Dict[str, Any]
    category: Optional[str]
    is_system: bool
    created_by: Optional[str]
    updated_by: Optional[str]
```

## 🚀 **API Endpoints**

### **Core CRUD Operations**
```bash
POST   /api/v2/project-attributes                    # Create
GET    /api/v2/project-attributes/                   # List (with filters)
GET    /api/v2/project-attributes/{key}              # Get by key
PUT    /api/v2/project-attributes/{key}              # Update
DELETE /api/v2/project-attributes/{key}              # Delete
```

### **Enhanced Filtering**
```bash
GET /api/v2/project-attributes/?key=monthly_disburse_lta&value_type=boolean&category=payroll
```

### **Category Operations**
```bash
GET /api/v2/project-attributes/category/{category}   # Get by category
```

### **Utility Endpoints**
```bash
GET /api/v2/project-attributes/boolean/{key}         # Get boolean value
GET /api/v2/project-attributes/numeric/{key}         # Get numeric value
GET /api/v2/project-attributes/string/{key}          # Get string value
```

### **Analytics & Summary**
```bash
GET /api/v2/project-attributes/summary               # Summary statistics
GET /api/v2/project-attributes/value-types           # Supported types
```

### **Bulk Operations**
```bash
POST /api/v2/project-attributes/bulk                 # Bulk creation
```

## 💡 **Usage Examples**

### **1. Boolean Flag Configuration**
```json
POST /api/v2/project-attributes
{
  "key": "monthly_disburse_lta",
  "value": true,
  "value_type": "boolean",
  "description": "Enable/disable monthly LTA disbursement",
  "category": "payroll",
  "is_system": true
}
```

### **2. Organization Contact Information**
```json
POST /api/v2/project-attributes
{
  "key": "org_phone",
  "value": "+91-9876543210",
  "value_type": "phone",
  "description": "Organization contact phone number",
  "category": "contact",
  "validation_rules": {"format": "international"}
}
```

### **3. Dropdown Configuration**
```json
POST /api/v2/project-attributes
{
  "key": "default_currency",
  "value": "INR",
  "value_type": "dropdown",
  "description": "Default currency for financial calculations",
  "category": "finance",
  "validation_rules": {
    "options": ["INR", "USD", "EUR", "GBP"]
  }
}
```

### **4. Numeric Configuration**
```json
POST /api/v2/project-attributes
{
  "key": "working_hours_per_day",
  "value": 8.0,
  "value_type": "number",
  "description": "Standard working hours per day",
  "category": "attendance",
  "validation_rules": {
    "min": 1,
    "max": 24
  }
}
```

## 🔧 **Integration in Code**

### **Using Project Attributes in Business Logic**

```python
# In a use case or service
class PayrollCalculationUseCase:
    def __init__(self, project_attributes_repo):
        self._repo = project_attributes_repo
    
    async def calculate_monthly_salary(self, employee_id: str, hostname: str):
        # Get boolean flag
        monthly_lta = await self._repo.get_boolean_attribute(
            "monthly_disburse_lta", hostname, default=False
        )
        
        # Get numeric configuration
        working_hours = await self._repo.get_numeric_attribute(
            "working_hours_per_day", hostname, default=8.0
        )
        
        # Get string configuration
        currency = await self._repo.get_string_attribute(
            "default_currency", hostname, default="INR"
        )
        
        # Use in calculations
        if monthly_lta:
            # Include LTA in monthly calculation
            pass
        
        # Apply working hours
        salary = base_salary * (working_hours / 8.0)
        
        return {
            "salary": salary,
            "currency": currency,
            "includes_lta": monthly_lta
        }
```

### **Using in Tax Calculations**

```python
class TaxCalculationService:
    def __init__(self, project_attributes_repo):
        self._repo = project_attributes_repo
    
    async def calculate_tax(self, employee_data: dict, hostname: str):
        # Check if perquisites are required
        perquisites_required = await self._repo.get_boolean_attribute(
            "perquisites_required", hostname, default=True
        )
        
        # Get tax year start month
        tax_year_start = await self._repo.get_string_attribute(
            "tax_year_start_month", hostname, default="4"
        )
        
        if perquisites_required:
            # Include perquisites in tax calculation
            pass
        
        # Use tax year configuration
        tax_year = self._calculate_tax_year(tax_year_start)
        
        return tax_calculation
```

## 📈 **Predefined Templates**

The system includes predefined attribute templates for common configurations:

1. **Payroll**
   - `monthly_disburse_lta` (boolean)
   - `working_hours_per_day` (number)

2. **Contact**
   - `org_phone` (phone)
   - `org_email` (email)
   - `org_address` (multiline_text)

3. **Taxation**
   - `perquisites_required` (boolean)
   - `tax_year_start_month` (dropdown)

4. **Finance**
   - `default_currency` (dropdown)

5. **Attendance**
   - `working_hours_per_day` (number)

## 🔐 **Security & Access Control**

- **Authentication**: JWT token required
- **Authorization**: Admin role required for write operations
- **Multi-tenancy**: Organization-based data isolation
- **Input Validation**: Comprehensive validation at multiple layers
- **Audit Trail**: Created/updated by tracking

## 🧪 **Validation Rules**

### **Type-Specific Validation**

1. **Boolean**: Must be true/false
2. **Number**: Must be numeric, optional min/max constraints
3. **Email**: Must contain @ symbol
4. **Phone**: Must be at least 10 characters
5. **URL**: Must start with http:// or https://
6. **Date**: Must be valid ISO format
7. **Dropdown**: Value must be in options list
8. **String/Text**: Optional max length constraints

### **Business Rule Validation**

- Key uniqueness per organization
- Key format (alphanumeric, underscores, hyphens)
- Length constraints (key: 100 chars, description: 500 chars, category: 50 chars)
- System attribute protection

## 📊 **Analytics & Monitoring**

### **Summary Statistics**
- Total attributes count
- Active/inactive distribution
- System vs custom attributes
- Type distribution
- Category distribution

### **Usage Tracking**
- Attribute access patterns
- Most used attributes
- Category usage statistics

## 🔄 **Migration & Deployment**

### **Database Schema**
```javascript
// MongoDB Collection: project_attributes
{
  "_id": ObjectId,
  "key": "string",
  "value": "mixed",
  "value_type": "string",
  "organisation_hostname": "string",
  "description": "string",
  "is_active": "boolean",
  "default_value": "mixed",
  "validation_rules": "object",
  "category": "string",
  "is_system": "boolean",
  "created_by": "string",
  "updated_by": "string",
  "created_at": "date",
  "updated_at": "date"
}
```

### **Indexes**
```javascript
// Compound index for efficient queries
db.project_attributes.createIndex({
  "organisation_hostname": 1,
  "key": 1
}, { unique: true })

// Category-based queries
db.project_attributes.createIndex({
  "organisation_hostname": 1,
  "category": 1
})

// Type-based queries
db.project_attributes.createIndex({
  "organisation_hostname": 1,
  "value_type": 1
})
```

## 🚀 **Future Enhancements**

1. **Attribute Dependencies**: Define relationships between attributes
2. **Versioning**: Track attribute value changes over time
3. **Templates**: Predefined attribute sets for different organization types
4. **Import/Export**: Bulk import/export configurations
5. **Caching**: Redis-based caching for frequently accessed attributes
6. **Webhooks**: Notify external systems of attribute changes
7. **Approval Workflow**: Multi-level approval for sensitive attributes
8. **Audit Logging**: Detailed audit trail for compliance

## 📝 **Best Practices**

1. **Naming Convention**: Use descriptive, lowercase keys with underscores
2. **Categories**: Group related attributes logically
3. **Validation**: Always define appropriate validation rules
4. **Defaults**: Provide sensible default values
5. **Documentation**: Use clear descriptions for all attributes
6. **Testing**: Test attribute retrieval in business logic
7. **Monitoring**: Monitor attribute usage and performance
8. **Backup**: Regular backup of configuration data

This enhanced implementation provides a robust, scalable solution for organization-specific configurations that can be easily integrated into any part of the application. 