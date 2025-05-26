# Payout Service Changes Summary

## Overview
Updated the `calculate_monthly_payout_service` function in `backend/app/services/payout_service.py` to address three key requirements:

## Changes Made

### 1. Date of Joining and Leaving Consideration
- **Before**: Pay period always started from the 1st and ended on the last day of the month
- **After**: Pay period considers both date of joining (DOJ) and date of leaving (DOL)
- **DOJ Logic**: 
  - If employee joined before the month: use month start (1st)
  - If employee joined during the month: use joining date as start
  - If employee joined after the month: return error
- **DOL Logic**:
  - If employee has no DOL (still active): use month end
  - If employee left before the month: return error
  - If employee left during the month: use leaving date as end
  - If employee left after the month: use month end
- **Proration**: Salary components are prorated based on actual working days ratio

### 2. Strict Taxation Data Requirement
- **Before**: Used `get_or_create_taxation_by_emp_id` which automatically created default tax data
- **After**: Uses `get_taxation_by_emp_id` which only retrieves existing data
- **Error Handling**: Returns HTTP 400 error with message "Please fill taxation data first" if no tax data exists

### 3. Removed Default Values
- **Before**: Used hardcoded defaults (300000, 120000, etc.) when tax data components were missing
- **After**: Validates that all required salary components exist in tax data
- **Validation**: Checks for required components: basic, dearness_allowance, hra, special_allowance
- **Error Handling**: Returns specific error listing missing components

## Technical Details

### Date Parsing
- Handles both ISO date formats: "YYYY-MM-DD" and "YYYY-MM-DDTHH:MM:SS"
- Validates date format and returns appropriate error messages
- Parses both DOJ and DOL (if present) with proper error handling

### Working Ratio Calculation
```python
total_days_in_month = calendar.monthrange(year, month)[1]
working_days_in_period = (pay_period_end - pay_period_start).days + 1
working_ratio = working_days_in_period / total_days_in_month
```

### Pay Period Validation
- Validates that pay period start is not after pay period end
- Ensures there are working days in the calculated period
- Handles edge cases like same-day joining and leaving

### Salary Proration
All salary components are multiplied by the working ratio:
- Basic Salary
- Dearness Allowance (DA)
- House Rent Allowance (HRA)
- Special Allowance
- Bonus
- Tax (TDS)

### Updated Notes Field
- **Before**: "Auto-calculated for MM/YYYY"
- **After**: "Auto-calculated for DD/MM/YYYY to DD/MM/YYYY" (shows actual pay period)

## Error Messages

1. **Missing Date of Joining**: "Employee {id} does not have a date of joining"
2. **Invalid DOJ Format**: "Invalid date of joining format for employee {id}"
3. **Invalid DOL Format**: "Invalid date of leaving format for employee {id}"
4. **Joined After Month**: "Employee {id} joined after MM/YYYY"
5. **Left Before Month**: "Employee {id} left before MM/YYYY"
6. **Invalid Employment Period**: "Employee {id} has invalid employment period for MM/YYYY"
7. **No Working Days**: "Employee {id} has no working days in MM/YYYY"
8. **No Tax Data**: "Taxation data not found for employee {id}. Please fill taxation data first."
9. **Missing Components**: "Missing salary components in taxation data for employee {id}: [components]. Please complete taxation data first."

## Impact on Other Functions

### Bulk Processing
- `bulk_process_monthly_payouts_service` will now capture and report these new error messages
- Employees without proper tax data will be listed in the errors array

### Scheduled Processing
- `process_monthly_payout_schedule_service` will handle errors gracefully
- Failed payouts will be logged with specific error reasons

## Backward Compatibility
- Legacy `PayoutService` class remains unchanged and uses the updated service functions
- All existing API endpoints continue to work with improved error handling

## Testing
- Date parsing logic tested with various formats (DOJ and DOL)
- Pay period calculation tested for different joining and leaving scenarios
- Working ratio calculation verified for partial months
- Edge cases tested: same-day joining/leaving, invalid periods, employees leaving before/after month
- Error handling verified for all invalid scenarios
- All tests pass successfully

## LWP (Leave Without Pay) Integration

### Additional Changes Made
- **LWP Calculation**: Integrated `calculate_lwp_for_month()` from employee_leave_service
- **Model Updates**: Added LWP tracking fields to PayoutBase and PayslipData models
- **Effective Working Days**: Salary calculated based on `effective_working_days = working_days - lwp_days`
- **Enhanced Reporting**: Payouts now include detailed attendance breakdown

### New Fields Added
```python
# Attendance and Working Days
total_days_in_month: int = Field(0, ge=0)
working_days_in_period: int = Field(0, ge=0)
lwp_days: int = Field(0, ge=0)
effective_working_days: int = Field(0, ge=0)
```

### LWP Impact on Calculations
- All salary components (basic, DA, HRA, special allowance, bonus) are prorated based on effective working ratio
- Tax calculations consider LWP deductions
- Payslips show detailed breakdown of working days vs LWP days

## Benefits
1. **Accurate Payroll**: Employees joining or leaving mid-month get correctly prorated salaries
2. **Complete Employment Lifecycle**: Handles both joining and leaving scenarios
3. **LWP Compliance**: Automatically deducts pay for unauthorized absences
4. **Data Integrity**: Ensures tax data is properly filled before payroll processing
5. **Better UX**: Clear error messages guide users to complete required data
6. **Compliance**: More accurate payroll calculations for statutory compliance
7. **Edge Case Handling**: Properly handles same-day joining/leaving and invalid periods
8. **Transparent Reporting**: Detailed attendance breakdown in payouts and payslips 