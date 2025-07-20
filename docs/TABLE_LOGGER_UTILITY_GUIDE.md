# Table Logger Utility Guide

## Overview

The Table Logger Utility provides a flexible and reusable way to create formatted tables in logs throughout the project. It supports multiple table styles, status indicators, and various formatting options.

## Features

- **Multiple Table Styles**: Unicode, Simple ASCII, Minimal, and Compact
- **Status Indicators**: Visual checkmarks (✓) and crosses (✗) for quick assessment
- **Flexible Column Configuration**: Custom widths, alignment, and formatters
- **Reusable Components**: Pre-built functions for common use cases
- **Consistent Formatting**: Standardized table appearance across the project

## Installation

The table logger is located at `backend/app/utils/table_logger.py` and is automatically available when you import it.

## Basic Usage

### 1. Import the Utility

```python
from app.utils.table_logger import (
    TableLogger, 
    log_taxation_breakdown, 
    log_salary_summary,
    log_attendance_table,
    log_simple_table
)
```

### 2. Using Pre-built Functions

#### Taxation Breakdown Table
```python
# For taxation exemptions and breakdowns
breakdown_items = [
    {'key': 'Hills Allowance', 'value': hills_exemption, 'status': hills_exemption.is_positive()},
    {'key': 'Border Allowance', 'value': border_exemption, 'status': border_exemption.is_positive()},
    # ... more items
]

log_taxation_breakdown("SPECIFIC ALLOWANCES EXEMPTIONS BREAKDOWN", breakdown_items)
```

#### Salary Summary Table
```python
# For salary component summaries
summary_data = {
    'Basic Salary': basic_salary,
    'Dearness Allowance': dearness_allowance,
    'HRA Provided': hra_provided,
    # ... more components
}

log_salary_summary("SALARY COMPONENTS SUMMARY", summary_data)
```

#### Simple Table
```python
# For basic data tables
headers = ['Employee ID', 'Name', 'Department', 'Salary']
data = [
    ['EMP001', 'John Doe', 'Engineering', '₹50,000'],
    ['EMP002', 'Jane Smith', 'Marketing', '₹45,000'],
]

log_simple_table("EMPLOYEE SALARY DATA", data, headers)
```

### 3. Using the TableLogger Class Directly

#### Creating Custom Tables
```python
from app.utils.table_logger import TableLogger, TableColumn

# Create table logger instance
table_logger = TableLogger(style=TableStyle.UNICODE)

# Define columns
columns = [
    TableColumn("Item", 25, "left"),
    TableColumn("Amount", 15, "right"),
    TableColumn("Status", 10, "center")
]

# Prepare data
data = [
    ["Basic Salary", "₹50,000", "✓"],
    ["HRA", "₹20,000", "✓"],
    ["Transport", "₹0", "✗"]
]

# Log the table
table_logger.log_table("SALARY BREAKDOWN", columns, data)
```

#### Status Indicators
```python
# Define status checker function
def check_positive_status(row_data):
    """Check if the amount in the row is positive."""
    amount = row_data[1]  # Amount is in second column
    return amount > 0

# Log table with status indicators
table_logger.log_table(
    title="SALARY COMPONENTS",
    columns=columns,
    data=data,
    show_status=True,
    status_checker=check_positive_status
)
```

## Table Styles

### 1. Unicode Style (Default)
```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                           SPECIFIC ALLOWANCES EXEMPTIONS BREAKDOWN                                   ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Allowance Type                    │  Exemption Amount  │  Status                                    ║
╟────────────────────────────────────┼───────────────────┼─────────────────────────────────────────────╢
║  Hills Allowance                   │  ₹1,200.00        │  ✓                                          ║
║  Border Allowance                  │  ₹0.00            │  ✗                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### 2. Simple ASCII Style
```
+--------------------------------+------------------+----------+
| Allowance Type                 | Exemption Amount | Status   |
+--------------------------------+------------------+----------+
| Hills Allowance                | ₹1,200.00       | ✓        |
| Border Allowance               | ₹0.00           | ✗        |
+--------------------------------+------------------+----------+
```

### 3. Minimal Style
```
Allowance Type                    Exemption Amount  Status
Hills Allowance                   ₹1,200.00        ✓
Border Allowance                  ₹0.00            ✗
```

## Use Cases Throughout the Project

### 1. Taxation Module
- **Salary Income**: Specific allowances exemptions breakdown
- **Tax Calculations**: Tax slab breakdowns and calculations
- **Deductions**: Section 80C, 80D, and other deduction summaries

### 2. Attendance Module
- **Attendance Records**: Daily attendance logs
- **Analytics**: Attendance statistics and summaries
- **Reports**: Monthly attendance reports

### 3. Leave Management
- **Leave Applications**: Leave request summaries
- **Leave Balances**: Employee leave balance tables
- **Approval Status**: Leave approval workflow status

### 4. Reporting Module
- **Dashboard Analytics**: Key metrics and KPIs
- **Export Reports**: Data export summaries
- **Performance Metrics**: Employee performance tables

### 5. User Management
- **User Lists**: Employee information tables
- **Role Assignments**: User role and permission summaries
- **Activity Logs**: User activity tracking

## Best Practices

### 1. Consistent Naming
```python
# Use descriptive titles
log_taxation_breakdown("SPECIFIC ALLOWANCES EXEMPTIONS BREAKDOWN", items)
log_salary_summary("MONTHLY SALARY COMPONENTS", summary)
```

### 2. Proper Data Structure
```python
# For breakdown tables
breakdown_items = [
    {'key': 'Item Name', 'value': amount, 'status': is_positive},
    # ...
]

# For summary tables
summary_data = {
    'Component Name': value,
    # ...
}
```

### 3. Status Indicators
```python
# Always include status for financial data
'status': amount.is_positive()  # For Money objects
'status': value > 0            # For numeric values
'status': bool(value)          # For boolean values
```

### 4. Column Alignment
```python
# Use appropriate alignment
TableColumn("Name", 25, "left")      # Text data
TableColumn("Amount", 15, "right")   # Numeric data
TableColumn("Status", 10, "center")  # Status indicators
```

## Migration Guide

### From Manual Table Formatting
```python
# Old way
s_logger.info(f"╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗")
s_logger.info(f"║  Allowance Type                    │  Exemption Amount  │  Status                                    ║")
s_logger.info(f"╟────────────────────────────────────┼───────────────────┼─────────────────────────────────────────────╢")
s_logger.info(f"║  Hills Allowance                   │  {hills_exemption:>15}  │  {'✓' if hills_exemption.is_positive() else '✗'}                                        ║")

# New way
breakdown_items = [
    {'key': 'Hills Allowance', 'value': hills_exemption, 'status': hills_exemption.is_positive()},
]
log_taxation_breakdown("SPECIFIC ALLOWANCES EXEMPTIONS BREAKDOWN", breakdown_items)
```

### From Simple Lists
```python
# Old way
s_logger.info(f"|Attribute                         |    Value|")
s_logger.info(f"|Monthly Hills Allowance           |{self.monthly_hills_allowance}|")

# New way
summary_data = {
    'Monthly Hills Allowance': self.monthly_hills_allowance,
}
log_salary_summary("SPECIFIC ALLOWANCES SUMMARY", summary_data)
```

## Configuration Options

### Environment Variables
```bash
# Log level for table output
LOG_LEVEL=INFO

# Log format (affects table appearance)
LOG_FORMAT=detailed  # or simple
```

### Custom Table Styles
```python
# Create custom table logger with specific style
table_logger = TableLogger(style=TableStyle.SIMPLE)

# Use in specific contexts where unicode might not display properly
```

## Troubleshooting

### Common Issues

1. **Unicode Display Issues**: Use `TableStyle.SIMPLE` for environments that don't support unicode
2. **Column Width Issues**: Ensure column widths are sufficient for your data
3. **Status Indicator Problems**: Make sure status checker function returns boolean values

### Debug Mode
```python
# Enable detailed logging for table operations
import logging
logging.getLogger('app.utils.table_logger').setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Export Options**: Add support for exporting tables to CSV/Excel
2. **Color Support**: Add colored output for different log levels
3. **Interactive Tables**: Support for interactive table viewing in web interfaces
4. **Chart Integration**: Combine tables with chart visualizations

## Examples

### Complete Example: Salary Processing
```python
from app.utils.table_logger import log_salary_summary, log_taxation_breakdown

def process_salary(employee_data):
    # Calculate salary components
    basic_salary = employee_data.get('basic_salary', 0)
    hra = employee_data.get('hra', 0)
    da = employee_data.get('da', 0)
    
    # Log salary summary
    summary_data = {
        'Basic Salary': basic_salary,
        'HRA': hra,
        'DA': da,
        'Total': basic_salary + hra + da
    }
    log_salary_summary("EMPLOYEE SALARY SUMMARY", summary_data)
    
    # Calculate and log exemptions
    exemptions = calculate_exemptions(employee_data)
    breakdown_items = [
        {'key': 'HRA Exemption', 'value': exemptions['hra'], 'status': exemptions['hra'] > 0},
        {'key': 'Transport Allowance', 'value': exemptions['transport'], 'status': exemptions['transport'] > 0},
    ]
    log_taxation_breakdown("SALARY EXEMPTIONS", breakdown_items)
```

This utility provides a consistent, maintainable, and visually appealing way to log tabular data throughout the project, making debugging and monitoring much easier. 