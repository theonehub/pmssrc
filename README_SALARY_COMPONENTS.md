# Salary Components Creation Scripts

This directory contains scripts to create salary components using the REST API.

## Files

- `create_salary_components.py` - Main script to create all salary components
- `test_api_connection.py` - Test script to verify API connectivity
- `requirements_script.txt` - Python dependencies for the scripts
- `README_SALARY_COMPONENTS.md` - This documentation file

## Prerequisites

1. **API Server Running**: The salary components API server should be running on port 8001
2. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r requirements_script.txt
   ```

## Usage

### Step 1: Test API Connection

Before creating components, test the API connectivity:

```bash
python test_api_connection.py
```

This will:
- Test connectivity to the API server
- Verify endpoint availability
- Check authentication requirements
- Provide diagnostic information

### Step 2: Create Salary Components

Run the main script to create all components:

```bash
python create_salary_components.py
```

The script will:
- Display a summary of components to be created
- Ask for confirmation before proceeding
- Create each component via REST API
- Provide detailed progress logs
- Show final statistics

## Components Created

The script creates the following types of components:

### Basic Salary Components (4)
- Basic Salary
- Dearness Allowance  
- Commission
- Bonus

### Fully Taxable Allowances (11)
Based on the provided list:
- City Compensatory Allowance
- Rural Allowance
- Proctorship Allowance
- Wardenship Allowance
- Project Allowance
- Deputation Allowance
- Overtime Allowance
- Interim Relief
- Tiffin Allowance
- Fixed Medical Allowance
- Servant Allowance

### Partially Exempt Allowances (4)
- House Rent Allowance (HRA) - Section 10(13A)
- Leave Travel Allowance (LTA) - Section 10(5)
- Conveyance Allowance - Section 10(14)
- Mobile Allowance - Section 17(2)

### Standard Deductions (4)
- Employee Provident Fund (PF) - 12% of basic
- Employee State Insurance (ESI) - 0.75% of gross
- Professional Tax - Fixed amount
- Income Tax (TDS) - Variable

### Reimbursements (3)
- Fuel Reimbursement
- Medical Reimbursement
- Travel Reimbursement

### Special Allowances (3)
- Performance Incentive
- Shift Allowance
- Special Allowance

**Total Components: ~29**

## Component Structure

Each component includes:
- `code`: Unique identifier (e.g., "BASIC_SALARY")
- `name`: Human-readable name
- `component_type`: EARNING, DEDUCTION, or REIMBURSEMENT
- `value_type`: FIXED, FORMULA, or VARIABLE
- `is_taxable`: Boolean indicating tax treatment
- `exemption_section`: Tax exemption section if applicable
- `formula`: Calculation formula for formula-based components
- `description`: Detailed description

## Configuration

### API Settings
Edit the scripts to modify:
- `BASE_URL`: API server URL (default: http://localhost:8001)
- `AUTH_TOKEN`: Authentication token if required

### Component Customization
To modify components:
1. Edit the `get_salary_components()` function in `create_salary_components.py`
2. Add, remove, or modify component definitions
3. Ensure all required fields are provided

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure API server is running on port 8001
   - Check network connectivity
   - Verify correct URL

2. **Authentication Required (401)**
   - Add authentication token to the script
   - Check user permissions

3. **Component Already Exists**
   - Components with duplicate codes will fail
   - Check existing components first
   - Modify codes if needed

4. **Invalid Data Format**
   - Verify all required fields are provided
   - Check data types match API expectations
   - Review API documentation

### Debugging

1. **Enable Verbose Logging**
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Test Individual Components**
   - Comment out other components in the list
   - Test one component at a time

3. **Check API Response**
   - Review error messages in logs
   - Check API server logs for details

## API Endpoints Used

- `GET /api/v2/salary-components/` - List existing components
- `POST /api/v2/salary-components/` - Create new component
- `GET /health` - Health check (if available)

## Example Usage

```bash
# 1. Install dependencies
pip install requests

# 2. Test API connection
python test_api_connection.py

# 3. Create all components
python create_salary_components.py

# 4. Verify creation (optional)
curl http://localhost:8001/api/v2/salary-components/
```

## Notes

- The script includes a small delay between API calls to avoid overwhelming the server
- Failed components are logged for review
- Components are created with sensible defaults
- Formula-based components include calculation logic
- Tax exemption sections are properly configured

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify API server status and configuration
3. Review component data for accuracy
4. Test with a single component first
