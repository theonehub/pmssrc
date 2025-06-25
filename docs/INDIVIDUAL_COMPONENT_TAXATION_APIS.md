# Individual Component Taxation APIs

## Overview

This document describes the new individual component taxation APIs that allow saving and updating different taxation components (salary, perquisites, deductions, etc.) separately under the taxation_record in the database for each employee.

## Key Features

- **Individual Component Updates**: Each taxation component can be updated independently
- **Automatic Record Creation**: If a taxation record doesn't exist, it's automatically created with defaults
- **Component Status Tracking**: Track the completion status of each component
- **Flexible Data Management**: Save components incrementally as data becomes available
- **Multi-tenant Support**: All operations are organization-scoped

## API Endpoints

### 1. Salary Component Management

#### Update Salary Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/salary
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "salary_income": {
    "basic_salary": 500000,
    "dearness_allowance": 50000,
    "hra_received": 240000,
    "hra_city_type": "metro",
    "actual_rent_paid": 300000,
    "bonus": 100000,
    "commission": 50000,
    "special_allowance": 200000
  },
  "notes": "Updated salary for Q4 increment"
}
```

**Response:**
```json
{
  "taxation_id": "tax_123456",
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "component_type": "salary_income",
  "status": "success",
  "message": "Salary component updated successfully",
  "updated_at": "2024-01-15T10:30:00Z",
  "notes": "Updated salary for Q4 increment"
}
```

### 2. Perquisites Component Management

#### Update Perquisites Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/perquisites
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "perquisites": {
    "accommodation": {
      "accommodation_type": "Employer-Owned",
      "city_population": "Above 40 lakhs",
      "basic_salary": 500000,
      "dearness_allowance": 50000
    },
    "car": {
      "car_use_type": "Personal",
      "engine_capacity_cc": 1600,
      "months_used": 12,
      "car_cost_to_employer": 800000
    },
    "medical_reimbursement": {
      "medical_reimbursement_amount": 15000,
      "is_overseas_treatment": false
    }
  },
  "notes": "Updated perquisites for FY 2024-25"
}
```

### 3. Deductions Component Management

#### Update Deductions Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/deductions
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "deductions": {
    "section_80c": {
      "life_insurance_premium": 15000,
      "epf_contribution": 60000,
      "ppf_contribution": 150000,
      "elss_investment": 50000,
      "home_loan_principal": 100000
    },
    "section_80d": {
      "self_family_premium": 25000,
      "parent_premium": 15000,
      "preventive_health_checkup": 5000
    },
    "section_80g": {
      "pm_relief_fund": 10000,
      "other_charitable_donations": 5000
    }
  },
  "notes": "Updated deductions for tax planning"
}
```

### 4. House Property Component Management

#### Update House Property Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/house-property
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "house_property_income": {
    "property_type": "Let-Out",
    "address": "123 Main Street, Mumbai",
    "annual_rent_received": 300000,
    "municipal_taxes_paid": 15000,
    "home_loan_interest": 200000,
    "pre_construction_interest": 50000
  },
  "notes": "Updated house property details"
}
```

### 5. Capital Gains Component Management

#### Update Capital Gains Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/capital-gains
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "capital_gains_income": {
    "stcg_111a_equity_stt": 50000,
    "stcg_other_assets": 25000,
    "ltcg_112a_equity_stt": 100000,
    "ltcg_other_assets": 75000
  },
  "notes": "Updated capital gains for FY 2024-25"
}
```

### 6. Retirement Benefits Component Management

#### Update Retirement Benefits Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/retirement-benefits
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "retirement_benefits": {
    "leave_encashment": {
      "leave_encashment_amount": 50000,
      "average_monthly_salary": 50000,
      "leave_days_encashed": 30,
      "is_govt_employee": false
    },
    "gratuity": {
      "gratuity_amount": 1000000,
      "monthly_salary": 50000,
      "service_years": 15,
      "is_govt_employee": false
    }
  },
  "notes": "Updated retirement benefits"
}
```

### 7. Other Income Component Management

#### Update Other Income Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/other-income
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "other_income": {
    "interest_income": {
      "savings_account_interest": 10000,
      "fixed_deposit_interest": 25000,
      "age": 35
    },
    "dividend_income": 15000,
    "gifts_received": 50000,
    "business_professional_income": 100000,
    "other_miscellaneous_income": 25000
  },
  "notes": "Updated other income sources"
}
```

### 8. Monthly Payroll Component Management

#### Update Monthly Payroll Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/monthly-payroll
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "monthly_payroll": {
    "employee_id": "emp123",
    "month": 4,
    "year": 2024,
    "basic_salary": 41667,
    "da": 4167,
    "hra": 20000,
    "special_allowance": 16667,
    "gross_salary": 82501,
    "net_salary": 70000,
    "tds": 5000,
    "tax_regime": "new",
    "effective_working_days": 22,
    "lwp_days": 0
  },
  "notes": "Updated monthly payroll for April 2024"
}
```

### 9. Tax Regime Component Management

#### Update Tax Regime Component
```http
PUT /api/v2/taxation/records/employee/{employee_id}/regime
```

**Request Body:**
```json
{
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "regime_type": "new",
  "age": 35,
  "notes": "Switched to new tax regime"
}
```

## Component Retrieval APIs

### Get Specific Component
```http
GET /api/v2/taxation/records/employee/{employee_id}/component/{component_type}?tax_year=2024-25
```

**Supported component types:**
- `salary_income`
- `perquisites`
- `deductions`
- `house_property_income`
- `capital_gains_income`
- `retirement_benefits`
- `other_income`
- `monthly_payroll`
- `regime`

**Response:**
```json
{
  "taxation_id": "tax_123456",
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "component_type": "salary_income",
  "component_data": {
    "basic_salary": 500000,
    "dearness_allowance": 50000,
    "hra_received": 240000,
    "hra_city_type": "metro",
    "actual_rent_paid": 300000,
    "bonus": 100000,
    "commission": 50000,
    "special_allowance": 200000
  },
  "last_updated": "2024-01-15T10:30:00Z",
  "notes": null
}
```

### Get Taxation Record Status
```http
GET /api/v2/taxation/records/employee/{employee_id}/status?tax_year=2024-25
```

**Response:**
```json
{
  "taxation_id": "tax_123456",
  "employee_id": "emp123",
  "tax_year": "2024-25",
  "regime_type": "new",
  "age": 35,
  "components_status": {
    "salary_income": {
      "has_data": true,
      "last_updated": "2024-01-15T10:30:00Z",
      "status": "complete"
    },
    "deductions": {
      "has_data": true,
      "last_updated": "2024-01-15T11:00:00Z",
      "status": "complete"
    },
    "perquisites": {
      "has_data": true,
      "last_updated": "2024-01-15T11:30:00Z",
      "status": "complete"
    },
    "house_property_income": {
      "has_data": false,
      "last_updated": null,
      "status": "not_provided"
    },
    "capital_gains_income": {
      "has_data": false,
      "last_updated": null,
      "status": "not_provided"
    },
    "retirement_benefits": {
      "has_data": false,
      "last_updated": null,
      "status": "not_provided"
    },
    "other_income": {
      "has_data": false,
      "last_updated": null,
      "status": "not_provided"
    },
    "monthly_payroll": {
      "has_data": false,
      "last_updated": null,
      "status": "not_provided"
    },
    "regime": {
      "has_data": true,
      "last_updated": "2024-01-15T10:00:00Z",
      "status": "complete",
      "regime_type": "new",
      "age": 35
    }
  },
  "overall_status": "partial_complete",
  "last_updated": "2024-01-15T11:30:00Z",
  "is_final": false
}
```

## Status Types

### Component Status
- `complete`: Component has been provided and is complete
- `not_provided`: Component has not been provided yet

### Overall Status
- `incomplete`: Required components (salary, deductions, regime) are missing
- `basic_complete`: Required components are complete, no optional components
- `partial_complete`: Required components + 1-2 optional components
- `comprehensive_complete`: Required components + 3+ optional components

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Employee ID in path must match employee_id in request body"
}
```

**404 Not Found:**
```json
{
  "detail": "Taxation record not found for employee emp123 and tax year 2024-25"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": "Invalid tax regime. Must be 'old' or 'new'"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to update salary component: Database connection error"
}
```

## Usage Examples

### Frontend Integration

```javascript
// Update salary component
const updateSalary = async (employeeId, taxYear, salaryData) => {
  const response = await fetch(`/api/v2/taxation/records/employee/${employeeId}/salary`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      employee_id: employeeId,
      tax_year: taxYear,
      salary_income: salaryData,
      notes: 'Updated via frontend'
    })
  });
  
  return await response.json();
};

// Get component status
const getStatus = async (employeeId, taxYear) => {
  const response = await fetch(`/api/v2/taxation/records/employee/${employeeId}/status?tax_year=${taxYear}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

### Progressive Data Entry

1. **Step 1**: Create basic record with regime
   ```http
   PUT /api/v2/taxation/records/employee/emp123/regime
   ```

2. **Step 2**: Add salary information
   ```http
   PUT /api/v2/taxation/records/employee/emp123/salary
   ```

3. **Step 3**: Add deductions
   ```http
   PUT /api/v2/taxation/records/employee/emp123/deductions
   ```

4. **Step 4**: Add optional components as needed
   ```http
   PUT /api/v2/taxation/records/employee/emp123/perquisites
   PUT /api/v2/taxation/records/employee/emp123/house-property
   ```

5. **Step 5**: Check overall status
   ```http
   GET /api/v2/taxation/records/employee/emp123/status?tax_year=2024-25
   ```

## Benefits

1. **Flexible Data Entry**: Components can be updated independently as data becomes available
2. **Progress Tracking**: Monitor completion status of each component
3. **Incremental Updates**: No need to provide all data at once
4. **Audit Trail**: Each update is timestamped and can include notes
5. **Multi-tenant**: All operations are properly scoped to organizations
6. **Backward Compatibility**: Works alongside existing comprehensive APIs

## Database Schema

The individual components are stored within the existing `taxation_records` collection:

```javascript
{
  "_id": ObjectId("..."),
  "taxation_id": "tax_123456",
  "employee_id": "emp123",
  "organization_id": "org_456",
  "tax_year": "2024-25",
  "age": 35,
  "regime": {
    "regime_type": "new"
  },
  "salary_income": { /* salary data */ },
  "deductions": { /* deductions data */ },
  "perquisites": { /* perquisites data */ },
  "other_income": {
    "house_property_income": { /* house property data */ },
    "capital_gains_income": { /* capital gains data */ },
    /* other income fields */
  },
  "retirement_benefits": { /* retirement benefits data */ },
  "monthly_payroll": { /* monthly payroll data */ },
  "created_at": ISODate("2024-01-15T10:00:00Z"),
  "updated_at": ISODate("2024-01-15T11:30:00Z"),
  "version": 1
}
```

## Security Considerations

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Users can only access records within their organization
3. **Input Validation**: All inputs are validated using Pydantic models
4. **Data Sanitization**: All monetary values are properly handled as Decimal
5. **Audit Logging**: All operations are logged for audit purposes

## Performance Considerations

1. **Efficient Updates**: Only the specific component is updated, not the entire record
2. **Indexing**: Proper indexes on employee_id, tax_year, and organization_id
3. **Caching**: Consider caching frequently accessed components
4. **Batch Operations**: For bulk updates, consider using the comprehensive APIs

## Migration Guide

### From Comprehensive APIs

If you're currently using the comprehensive taxation APIs, you can gradually migrate to individual component APIs:

1. **Phase 1**: Use individual APIs for new records
2. **Phase 2**: Migrate existing records component by component
3. **Phase 3**: Use status API to track migration progress

### Example Migration Script

```python
async def migrate_to_individual_components(employee_id, tax_year, organization_id):
    # Get existing comprehensive record
    comprehensive_record = await get_comprehensive_record(employee_id, tax_year)
    
    # Update individual components
    await update_salary_component(employee_id, tax_year, comprehensive_record.salary_income)
    await update_deductions_component(employee_id, tax_year, comprehensive_record.deductions)
    await update_perquisites_component(employee_id, tax_year, comprehensive_record.perquisites)
    
    # Check status
    status = await get_taxation_record_status(employee_id, tax_year)
    print(f"Migration status: {status.overall_status}") 