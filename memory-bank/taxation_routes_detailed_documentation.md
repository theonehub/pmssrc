# Taxation Routes - Detailed API Documentation

## Overview
This document provides a comprehensive analysis of the `taxation_routes.py` file, detailing each endpoint with their complete data structures, input parameters, and response formats. The API follows RESTful principles and implements clean architecture with SOLID principles for comprehensive taxation operations.

## Base URL
All endpoints are prefixed with `/v2/taxation`

---

## 1. Individual Component Update Endpoints

### 1.1 PUT `/v2/taxation/records/employee/{employee_id}/salary`
**Purpose**: Update salary component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateSalaryComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "basic_salary": "float",
  "hra": "float",
  "da": "float",
  "special_allowance": "float",
  "other_allowances": "float",
  "arrears": "float",
  "bonus": "float",
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Response Structure**:
```json
{
  "success": "boolean",
  "message": "string",
  "employee_id": "string",
  "tax_year": "string",
  "component_type": "string",
  "updated_at": "string (ISO datetime)",
  "updated_by": "string"
}
```

**Error Responses**:
- `400`: Employee ID mismatch between path and body
- `422`: Validation error
- `500`: Internal server error

---

### 1.2 PUT `/v2/taxation/records/employee/{employee_id}/perquisites`
**Purpose**: Update perquisites component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdatePerquisitesComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "accommodation": {
    "type": "string",
    "city_category": "string",
    "amount": "float"
  },
  "car": {
    "type": "string",
    "usage": "string",
    "engine_capacity": "float",
    "amount": "float"
  },
  "lta": {
    "amount": "float",
    "exemption": "float"
  },
  "interest_free_loan": {
    "amount": "float",
    "sbi_rate": "float"
  },
  "esop": {
    "amount": "float"
  },
  "other_perquisites": "float",
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Error Responses**:
- `400`: Employee ID mismatch
- `422`: Validation error
- `500`: Internal server error

---

### 1.3 PUT `/v2/taxation/records/employee/{employee_id}/deductions`
**Purpose**: Update deductions component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateDeductionsComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "section_80c": {
    "elss": "float",
    "ppf": "float",
    "lic": "float",
    "nps": "float",
    "sukanya_samriddhi": "float",
    "senior_citizen_savings": "float",
    "post_office_savings": "float",
    "ulip": "float",
    "home_loan_principal": "float",
    "stamp_duty_registration": "float",
    "tuition_fees": "float"
  },
  "section_80d": {
    "health_insurance_premium": "float",
    "preventive_health_checkup": "float",
    "medical_expenses_senior_citizen": "float"
  },
  "section_80g": {
    "donations": "float"
  },
  "section_80e": {
    "education_loan_interest": "float"
  },
  "section_80tta": {
    "savings_account_interest": "float"
  },
  "section_80g": {
    "donations": "float"
  },
  "section_80ccd": {
    "nps_contribution": "float"
  },
  "section_80jjaa": {
    "employment_generation": "float"
  },
  "section_80d": {
    "health_insurance_premium": "float",
    "preventive_health_checkup": "float",
    "medical_expenses_senior_citizen": "float"
  },
  "section_80e": {
    "education_loan_interest": "float"
  },
  "section_80tta": {
    "savings_account_interest": "float"
  },
  "section_80ccd": {
    "nps_contribution": "float"
  },
  "section_80jjaa": {
    "employment_generation": "float"
  },
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Error Responses**:
- `400`: Employee ID mismatch
- `404`: Taxation record not found
- `409`: Attempted to update finalized record
- `422`: Validation error
- `500`: Internal server error

---

### 1.4 PUT `/v2/taxation/records/employee/{employee_id}/house-property`
**Purpose**: Update house property income component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateHousePropertyComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "properties": [
    {
      "property_type": "string",
      "annual_value": "float",
      "municipal_taxes": "float",
      "interest_on_borrowed_capital": "float",
      "standard_deduction": "float",
      "net_annual_value": "float",
      "income_from_house_property": "float"
    }
  ],
  "total_income_from_house_property": "float",
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Error Responses**:
- `400`: Employee ID mismatch
- `422`: Validation error
- `500`: Internal server error

---

### 1.5 PUT `/v2/taxation/records/employee/{employee_id}/capital-gains`
**Purpose**: Update capital gains income component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateCapitalGainsComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "short_term_capital_gains": {
    "equity_with_stt": "float",
    "other_assets": "float"
  },
  "long_term_capital_gains": {
    "equity_with_stt": "float",
    "other_assets": "float"
  },
  "total_capital_gains": "float",
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Error Responses**:
- `400`: Employee ID mismatch
- `422`: Validation error
- `500`: Internal server error

---

### 1.6 PUT `/v2/taxation/records/employee/{employee_id}/retirement-benefits`
**Purpose**: Update retirement benefits component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateRetirementBenefitsComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "leave_encashment": {
    "amount": "float",
    "exemption": "float",
    "taxable_amount": "float"
  },
  "gratuity": {
    "amount": "float",
    "exemption": "float",
    "taxable_amount": "float"
  },
  "vrs": {
    "amount": "float",
    "exemption": "float",
    "taxable_amount": "float"
  },
  "total_retirement_benefits": "float",
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Error Responses**:
- `400`: Employee ID mismatch
- `422`: Validation error
- `500`: Internal server error

---

### 1.7 PUT `/v2/taxation/records/employee/{employee_id}/other-income`
**Purpose**: Update other income component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateOtherIncomeComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "interest_income": "float",
  "dividend_income": "float",
  "rental_income": "float",
  "business_income": "float",
  "professional_income": "float",
  "other_income": "float",
  "total_other_income": "float",
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Error Responses**:
- `400`: Employee ID mismatch
- `422`: Validation error
- `500`: Internal server error

---

### 1.8 PUT `/v2/taxation/records/employee/{employee_id}/monthly-payroll`
**Purpose**: Update monthly payroll component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateMonthlyPayrollComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "month": "integer",
  "basic_salary": "float",
  "hra": "float",
  "da": "float",
  "special_allowance": "float",
  "other_allowances": "float",
  "arrears": "float",
  "bonus": "float",
  "gross_salary": "float",
  "pf_contribution": "float",
  "professional_tax": "float",
  "other_deductions": "float",
  "net_salary": "float",
  "tds": "float",
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Error Responses**:
- `400`: Employee ID mismatch
- `422`: Validation error
- `500`: Internal server error

---

### 1.9 GET `/v2/taxation/records/employee/{employee_id}/regime/allowed`
**Purpose**: Check if regime update is allowed

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Query Parameters**:
- `tax_year` (string, required): Tax year (e.g., '2024-25')

**Response**: IsRegimeUpdateAllowedResponse

**Response Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "is_allowed": "boolean",
  "reason": "string (optional)",
  "current_regime": "string (optional)",
  "restrictions": ["string[]"]
}
```

**Error Responses**:
- `500`: Internal server error

---

### 1.10 PUT `/v2/taxation/records/employee/{employee_id}/regime`
**Purpose**: Update tax regime component individually

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateRegimeComponentRequest

**Request Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "regime": "string",
  "age": "integer",
  "notes": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response**: ComponentUpdateResponse

**Error Responses**:
- `400`: Employee ID mismatch
- `422`: Validation error
- `500`: Internal server error

---

## 2. Component Retrieval Endpoints

### 2.1 GET `/v2/taxation/records/employee/{employee_id}/component/{component_type}`
**Purpose**: Get specific component from taxation record

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID
- `component_type` (string, required): Component type (salary, perquisites, deductions, etc.)

**Query Parameters**:
- `tax_year` (string, required): Tax year (e.g., '2024-25')

**Response**: ComponentResponse

**Response Structure**:
```json
{
  "employee_id": "string",
  "tax_year": "string",
  "component_type": "string",
  "component_data": "object",
  "last_updated": "string (ISO datetime)",
  "updated_by": "string",
  "is_finalized": "boolean"
}
```

**Error Responses**:
- `404`: Component not found
- `500`: Internal server error

---

## 3. Employee Selection Endpoints

### 3.1 GET `/v2/taxation/employees/selection`
**Purpose**: Get employees for taxation selection

**Authentication**: Required (CurrentUser)

**Query Parameters**:
- `skip` (integer, optional, default: 0): Number of records to skip
- `limit` (integer, optional, default: 20, max: 100): Maximum number of records to return
- `search` (string, optional): Search term for employee name or email
- `department` (string, optional): Filter by department
- `role` (string, optional): Filter by role
- `employee_status` (string, optional): Filter by employee status
- `has_tax_record` (boolean, optional): Filter by tax record availability
- `tax_year` (string, optional): Filter by tax year

**Response**: EmployeeSelectionResponse

**Response Structure**:
```json
{
  "employees": [
    {
      "employee_id": "string",
      "name": "string",
      "email": "string",
      "department": "string",
      "designation": "string",
      "status": "string",
      "has_tax_record": "boolean",
      "tax_year": "string",
      "last_updated": "string (ISO datetime)",
      "completion_percentage": "float"
    }
  ],
  "total": "integer",
  "filtered_count": "integer",
  "pagination": {
    "page": "integer",
    "page_size": "integer",
    "total_pages": "integer",
    "has_next": "boolean",
    "has_previous": "boolean"
  }
}
```

**Error Responses**:
- `400`: Invalid input parameters
- `500`: Internal server error

---

## 4. Information and Utility Endpoints

### 4.1 GET `/v2/taxation/tax-regimes/comparison`
**Purpose**: Compare tax regimes

**Authentication**: Not required

**Response Structure**:
```json
{
  "regime_comparison": {
    "old_regime": {
      "description": "string",
      "deductions_available": "boolean",
      "exemptions_available": "boolean",
      "perquisites_taxable": "boolean",
      "standard_deduction": "integer",
      "popular_deductions": ["string[]"]
    },
    "new_regime": {
      "description": "string",
      "deductions_available": "boolean",
      "exemptions_limited": "boolean",
      "perquisites_taxable": "boolean",
      "standard_deduction": "integer",
      "limited_deductions": ["string[]"]
    }
  },
  "tax_slabs_2024_25": {
    "old_regime": [
      {
        "range": "string",
        "rate": "string"
      }
    ],
    "new_regime": [
      {
        "range": "string",
        "rate": "string"
      }
    ]
  },
  "recommendation": "string"
}
```

---

### 4.2 GET `/v2/taxation/perquisites/types`
**Purpose**: Get perquisites types

**Authentication**: Not required

**Response Structure**:
```json
{
  "perquisite_types": {
    "core_perquisites": {
      "accommodation": {
        "description": "string",
        "types": ["string[]"],
        "city_categories": ["string[]"]
      },
      "car": {
        "description": "string",
        "usage_types": ["string[]"],
        "engine_capacity_matters": "boolean"
      }
    },
    "medical_travel": {
      "lta": {
        "description": "string",
        "exemption_conditions": "string"
      }
    },
    "financial_perquisites": {
      "interest_free_loan": {
        "description": "string",
        "sbi_rate_applicable": "boolean"
      },
      "esop": {
        "description": "string",
        "taxation_on_exercise": "boolean"
      }
    }
  },
  "applicability": {
    "old_regime": "string",
    "new_regime": "string"
  }
}
```

---

### 4.3 GET `/v2/taxation/capital-gains/rates`
**Purpose**: Get capital gains tax rates

**Authentication**: Not required

**Response Structure**:
```json
{
  "short_term_capital_gains": {
    "equity_with_stt": {
      "rate": "string",
      "description": "string"
    },
    "other_assets": {
      "rate": "string",
      "description": "string"
    }
  },
  "long_term_capital_gains": {
    "equity_with_stt": {
      "rate": "string",
      "description": "string",
      "exemption": "string"
    },
    "other_assets": {
      "rate": "string",
      "description": "string"
    }
  },
  "holding_periods": {
    "equity_shares": "string",
    "debt_instruments": "string",
    "real_estate": "string"
  }
}
```

---

### 4.4 GET `/v2/taxation/retirement-benefits/info`
**Purpose**: Get retirement benefits information

**Authentication**: Not required

**Response Structure**:
```json
{
  "retirement_benefits": {
    "leave_encashment": {
      "description": "string",
      "exemption_govt": "string",
      "exemption_private": "string"
    },
    "gratuity": {
      "description": "string",
      "exemption_govt": "string",
      "exemption_private": "string"
    },
    "vrs": {
      "description": "string",
      "exemption": "string"
    }
  }
}
```

---

### 4.5 GET `/v2/taxation/tax-years`
**Purpose**: Get available tax years

**Authentication**: Not required

**Response Structure**:
```json
[
  {
    "value": "string",
    "display_name": "string",
    "assessment_year": "string",
    "is_current": "boolean"
  }
]
```

---

### 4.6 GET `/v2/taxation/health`
**Purpose**: Health check for taxation service

**Authentication**: Not required

**Response Structure**:
```json
{
  "status": "string",
  "message": "string",
  "timestamp": "string (ISO datetime)"
}
```

---

## 5. Monthly Tax Computation Endpoints

### 5.1 GET `/v2/taxation/monthly-tax/employee/{employee_id}`
**Purpose**: Compute monthly tax for employee

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Response Structure**:
```json
{
  "employee_id": "string",
  "month": "integer",
  "year": "integer",
  "basic_salary": "float",
  "hra": "float",
  "da": "float",
  "special_allowance": "float",
  "other_allowances": "float",
  "gross_salary": "float",
  "pf_contribution": "float",
  "professional_tax": "float",
  "other_deductions": "float",
  "net_salary": "float",
  "tds": "float",
  "tax_regime": "string",
  "computed_at": "string (ISO datetime)"
}
```

**Error Responses**:
- `422`: Validation error
- `500`: Internal server error

---

### 5.2 GET `/v2/taxation/monthly-tax/current/{employee_id}`
**Purpose**: Compute current month tax for employee

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Response**: Same as monthly-tax endpoint

**Error Responses**:
- `422`: Validation error
- `500`: Internal server error

---

### 5.3 GET `/v2/taxation/export/salary-package/{employee_id}`
**Purpose**: Export comprehensive salary package to Excel (multiple sheets)

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Query Parameters**:
- `tax_year` (string, optional): Tax year (e.g., '2025-26')

**Response**: Excel file download

**Error Responses**:
- `500`: Failed to export salary package

---

### 5.4 GET `/v2/taxation/export/salary-package-single/{employee_id}`
**Purpose**: Export comprehensive salary package to Excel (single sheet)

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Query Parameters**:
- `tax_year` (string, optional): Tax year (e.g., '2025-26')

**Response**: Excel file download

**Error Responses**:
- `500`: Failed to export salary package

---

## 6. Monthly Salary Computation Endpoints

### 6.1 POST `/v2/taxation/monthly-salary/compute`
**Purpose**: Compute monthly salary for employee

**Authentication**: Required (CurrentUser)

**Request Body**: MonthlySalaryComputeRequestDTO

**Request Structure**:
```json
{
  "employee_id": "string",
  "month": "integer",
  "year": "integer",
  "tax_year": "string",
  "basic_salary": "float",
  "hra": "float",
  "da": "float",
  "special_allowance": "float",
  "other_allowances": "float",
  "arrears": "float",
  "bonus": "float",
  "pf_contribution": "float",
  "professional_tax": "float",
  "other_deductions": "float",
  "tax_regime": "string",
  "notes": "string (optional)"
}
```

**Response**: MonthlySalaryResponseDTO

**Response Structure**:
```json
{
  "employee_id": "string",
  "month": "integer",
  "year": "integer",
  "tax_year": "string",
  "basic_salary": "float",
  "hra": "float",
  "da": "float",
  "special_allowance": "float",
  "other_allowances": "float",
  "arrears": "float",
  "bonus": "float",
  "gross_salary": "float",
  "pf_contribution": "float",
  "professional_tax": "float",
  "other_deductions": "float",
  "net_salary": "float",
  "tds": "float",
  "tax_regime": "string",
  "status": "string",
  "computed_at": "string (ISO datetime)",
  "computed_by": "string",
  "payout_status": {
    "status": "string",
    "comments": "string",
    "transaction_id": "string",
    "transfer_date": "string (ISO date)"
  },
  "tds_status": {
    "status": "string",
    "challan_number": "string",
    "filed_date": "string (ISO date)"
  }
}
```

**Error Responses**:
- `422`: Validation error
- `500`: Internal server error

---

### 6.2 GET `/v2/taxation/monthly-salary/employee/{employee_id}/month/{month}/year/{year}`
**Purpose**: Get monthly salary for employee

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID
- `month` (integer, required): Month number (1-12)
- `year` (integer, required): Year

**Response**: MonthlySalaryResponseDTO

**Error Responses**:
- `404`: Salary not found
- `500`: Internal server error

---

### 6.3 GET `/v2/taxation/monthly-salary/employee/{employee_id}/history`
**Purpose**: Get salary history for employee

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Query Parameters**:
- `limit` (integer, optional, default: 100, max: 200): Maximum number of records to return
- `offset` (integer, optional, default: 0): Number of records to skip

**Response**: List[MonthlySalaryResponseDTO]

**Error Responses**:
- `500`: Internal server error

---

### 6.4 GET `/v2/taxation/monthly-salary/employee/{employee_id}/month/{month}/year/{year}/payslip`
**Purpose**: Download payslip for employee

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID
- `month` (integer, required): Month number (1-12)
- `year` (integer, required): Year

**Response**: PDF file download

**Error Responses**:
- `404`: Payslip not found
- `500`: Internal server error

---

### 6.5 GET `/v2/taxation/monthly-salary/period/month/{month}/tax-year/{tax_year}`
**Purpose**: Get monthly salaries for period

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `month` (integer, required): Month number (1-12)
- `tax_year` (string, required): Tax year (e.g., '2024-25')

**Query Parameters**:
- `salary_status` (string, optional): Filter by status
- `department` (string, optional): Filter by department
- `skip` (integer, optional, default: 0): Number of records to skip
- `limit` (integer, optional, default: 20, max: 100): Maximum number of records to return

**Response Structure**:
```json
{
  "salaries": ["MonthlySalaryResponseDTO[]"],
  "total": "integer",
  "filtered_count": "integer",
  "pagination": {
    "page": "integer",
    "page_size": "integer",
    "total_pages": "integer",
    "has_next": "boolean",
    "has_previous": "boolean"
  }
}
```

**Error Responses**:
- `500`: Internal server error

---

### 6.6 GET `/v2/taxation/monthly-salary/summary/month/{month}/tax-year/{tax_year}`
**Purpose**: Get monthly salary summary

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `month` (integer, required): Month number (1-12)
- `tax_year` (string, required): Tax year (e.g., '2024-25')

**Response Structure**:
```json
{
  "month": "integer",
  "tax_year": "string",
  "total_employees": "integer",
  "total_gross_salary": "float",
  "total_net_salary": "float",
  "total_tds": "float",
  "average_salary": "float",
  "status_distribution": {
    "computed": "integer",
    "approved": "integer",
    "transferred": "integer",
    "pending": "integer"
  },
  "department_summary": [
    {
      "department": "string",
      "employee_count": "integer",
      "total_salary": "float",
      "average_salary": "float"
    }
  ]
}
```

**Error Responses**:
- `500`: Internal server error

---

### 6.7 POST `/v2/taxation/monthly-salary/bulk-compute`
**Purpose**: Bulk compute monthly salaries

**Authentication**: Required (CurrentUser)

**Request Body**: Dict[str, Any]

**Request Structure**:
```json
{
  "employee_ids": ["string[]"],
  "month": "integer",
  "year": "integer",
  "tax_year": "string",
  "options": {
    "include_arrears": "boolean",
    "include_bonus": "boolean",
    "tax_regime": "string"
  }
}
```

**Response Structure**:
```json
{
  "total_requested": "integer",
  "successful": "integer",
  "failed": "integer",
  "skipped": "integer",
  "errors": ["string[]"],
  "computation_summary": "object"
}
```

**Error Responses**:
- `500`: Internal server error

---

### 6.8 PUT `/v2/taxation/monthly-salary/status`
**Purpose**: Update monthly salary status

**Authentication**: Required (CurrentUser)

**Request Body**: Dict[str, Any]

**Request Structure**:
```json
{
  "employee_id": "string",
  "month": "integer",
  "year": "integer",
  "status": "string",
  "comments": "string (optional)",
  "transaction_id": "string (optional)",
  "transfer_date": "string (ISO date, optional)",
  "tds_status": "string (optional)",
  "challan_number": "string (optional)"
}
```

**Response**: MonthlySalaryResponseDTO

**Error Responses**:
- `400`: Invalid request
- `404`: Salary record not found
- `500`: Internal server error

---

### 6.9 PUT `/v2/taxation/monthly-salary/payment`
**Purpose**: Mark monthly salary payment

**Authentication**: Required (CurrentUser)

**Request Body**: Dict[str, Any]

**Response**: MonthlySalaryResponseDTO

**Error Responses**:
- `501`: Not implemented
- `500`: Internal server error

---

## 7. Loan Processing Endpoints

### 7.1 GET `/v2/taxation/loan-schedule/employee/{employee_id}`
**Purpose**: Process loan schedule for employee

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Query Parameters**:
- `tax_year` (string, required): Tax year (e.g., '2024-25')

**Response Structure**:
```json
{
  "employee": {
    "employee_id": "string",
    "name": "string",
    "email": "string",
    "department": "string"
  },
  "loan_details": {
    "loan_amount": "float",
    "emi_amount": "float",
    "company_rate": "float",
    "sbi_rate": "float",
    "loan_type": "string",
    "start_date": "string (ISO date)",
    "end_date": "string (ISO date)"
  },
  "monthly_schedules": {
    "company_rate": [
      {
        "month": "integer",
        "year": "integer",
        "opening_balance": "float",
        "emi_payment": "float",
        "interest_payment": "float",
        "principal_payment": "float",
        "closing_balance": "float"
      }
    ],
    "sbi_rate": [
      {
        "month": "integer",
        "year": "integer",
        "opening_balance": "float",
        "emi_payment": "float",
        "interest_payment": "float",
        "principal_payment": "float",
        "closing_balance": "float"
      }
    ]
  },
  "interest_calculations": {
    "total_interest_company_rate": "float",
    "total_interest_sbi_rate": "float",
    "interest_savings": "float",
    "tax_benefit": "float"
  },
  "summary": {
    "total_emi_payments": "float",
    "total_interest_payments": "float",
    "total_principal_payments": "float",
    "loan_duration_months": "integer",
    "effective_interest_rate": "float"
  }
}
```

**Error Responses**:
- `422`: Validation error
- `500`: Internal server error

---

## 8. Data Transfer Objects (DTOs) Summary

### Request DTOs:
1. **UpdateSalaryComponentRequest**: For updating salary components
2. **UpdatePerquisitesComponentRequest**: For updating perquisites
3. **UpdateDeductionsComponentRequest**: For updating deductions
4. **UpdateHousePropertyComponentRequest**: For updating house property income
5. **UpdateCapitalGainsComponentRequest**: For updating capital gains
6. **UpdateRetirementBenefitsComponentRequest**: For updating retirement benefits
7. **UpdateOtherIncomeComponentRequest**: For updating other income
8. **UpdateMonthlyPayrollComponentRequest**: For updating monthly payroll
9. **UpdateRegimeComponentRequest**: For updating tax regime
10. **IsRegimeUpdateAllowedRequest**: For checking regime update eligibility
11. **MonthlySalaryComputeRequestDTO**: For computing monthly salary
12. **EmployeeSelectionQuery**: For employee selection queries

### Response DTOs:
1. **ComponentUpdateResponse**: Response for component updates
2. **ComponentResponse**: Response for component retrieval
3. **IsRegimeUpdateAllowedResponse**: Response for regime update check
4. **MonthlySalaryResponseDTO**: Response for monthly salary operations
5. **EmployeeSelectionResponse**: Response for employee selection
6. **TaxationRecordStatusResponse**: Response for record status

## 9. Error Handling

All endpoints follow consistent error handling patterns:

- **400 Bad Request**: Invalid input data or employee ID mismatch
- **404 Not Found**: Component or record not found
- **409 Conflict**: Attempted to update finalized record
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server-side errors
- **501 Not Implemented**: Functionality not yet implemented

## 10. Authentication and Authorization

Most endpoints require authentication via `CurrentUser` dependency. Information endpoints (tax regimes, perquisites types, etc.) are publicly accessible.

## 11. File Export Support

The API supports file exports for:
- Salary package data (Excel with multiple sheets)
- Salary package data (Excel with single sheet)
- Payslip PDFs

## 12. Tax Regime Support

The API supports both old and new tax regimes with:
- Automatic regime selection based on deductions
- Regime comparison information
- Regime-specific calculations

## 13. Component Types

Supported component types for individual updates:
- `salary`: Basic salary and allowances
- `perquisites`: Employer-provided benefits
- `deductions`: Tax-saving investments and expenses
- `house_property`: Income from house property
- `capital_gains`: Capital gains income
- `retirement_benefits`: Retirement-related income
- `other_income`: Other sources of income
- `monthly_payroll`: Monthly salary breakdown
- `regime`: Tax regime and age

## 14. Monthly Salary Features

Comprehensive monthly salary processing with:
- Gross to net salary calculation
- TDS computation
- Multiple tax regime support
- Arrears and bonus handling
- Status tracking (computed, approved, transferred)
- Payslip generation
- Bulk processing capabilities

## 15. Loan Processing Features

Advanced loan schedule processing with:
- EMI calculation
- Interest computation (company vs SBI rates)
- Tax benefit calculations
- Monthly payment schedules
- Interest savings analysis

This comprehensive API provides complete taxation functionality with proper validation, error handling, and support for all major Indian tax components and calculations. 