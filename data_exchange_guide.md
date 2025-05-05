# Data Exchange Standardization Guide

This document outlines the standardized approach for data exchange between the frontend and backend components of our application.

## General Principles

1. Use **JSON for most data exchanges** unless there's a specific reason not to (e.g., file uploads, authentication)
2. Use **multipart/form-data only for file uploads**
3. Use utility functions for all API requests to maintain consistency

## Backend Guidelines

### JSON Data Handling

For endpoints that receive JSON data:

1. Use Pydantic models with `Body()` parameter in FastAPI
2. Example:
   ```python
   @router.post("/resource")
   def create_resource(
       data: ResourceModel = Body(...),
       current_user: str = Depends(get_current_user)
   ):
       # Process data
       return {"message": "Resource created"}
   ```

### File Upload Handling

For endpoints that handle file uploads:

1. Create separate endpoints with a `/with-file` suffix for the same resource
2. Use `Form()` and `File()` parameters in FastAPI
3. Example:
   ```python
   @router.post("/resource/with-file")
   async def create_resource_with_file(
       field1: str = Form(...),
       field2: str = Form(...),
       file: UploadFile = File(...),
       current_user: str = Depends(get_current_user)
   ):
       # Process file and data
       return {"message": "Resource with file created"}
   ```

### File Handling Utilities

Use the provided file handling utilities:

1. `validate_file()` - Validates file type and size
2. `save_file()` - Saves file to appropriate directory
3. Make file processing functions `async` to handle properly

## Frontend Guidelines

### API Utility Usage

Use the `apiUtils.js` file for all API requests:

```javascript
import api from '../../utils/apiUtils';

// GET request
const data = await api.get('/endpoint');

// POST with JSON
await api.post('/resource', { field1: 'value', field2: 'value' });

// PUT with JSON
await api.put(`/resource/${id}`, { field1: 'value', field2: 'value' });

// DELETE request
await api.delete(`/resource/${id}`);

// File upload with form data
await api.upload(
  '/resource/with-file',
  fileObject,
  { field1: 'value', field2: 'value' }
);

// Multiple file upload
await api.uploadMultiple(
  '/resource/with-files',
  { file1: fileObject1, file2: fileObject2 },
  { field1: 'value', field2: 'value' }
);
```

### File Uploads

When handling file uploads:

1. Check if a file is present
2. Use `api.upload()` for single file uploads
3. Use `api.uploadMultiple()` for multiple file uploads
4. Use `api.post()` or `api.put()` for requests without files
5. Example:
   ```javascript
   if (formData.file) {
     // File upload approach
     await api.upload(
       '/resource/with-file',
       formData.file,
       {
         field1: formData.field1,
         field2: formData.field2
       }
     );
   } else {
     // JSON approach
     await api.post('/resource', {
       field1: formData.field1,
       field2: formData.field2
     });
   }
   ```

## Authentication

For authentication endpoints:

1. Continue using `application/x-www-form-urlencoded` for OAuth-style authentication
2. The login endpoint should remain as is, using `URLSearchParams`

## Implementation Examples

### User Management Module

The User Management module demonstrates our standardized approach:

#### Backend Implementation

```python
# JSON endpoint for creating users without files
@router.post("/users")
async def create_user(
    data: UserInfo = Body(...),
    current_user: str = Depends(extract_emp_id)
):
    # Process user data
    return result

# File upload endpoint with /with-files suffix
@router.post("/users/with-files")
async def create_user_with_files(
    user_data: str = Form(...),
    pan_file: UploadFile = File(None),
    aadhar_file: UploadFile = File(None),
    photo: UploadFile = File(None),
    current_user: str = Depends(extract_emp_id)
):
    # Process user data with files
    # Use validate_file and save_file utilities
    return result
```

#### Frontend Implementation

```javascript
// UsersList.jsx
const handleCreateUser = async (e) => {
  e.preventDefault();
  
  // Extract user data
  const userData = {
    // Form fields
  };

  // Get file uploads if any
  const panFile = e.target.pan_file.files[0];
  const aadharFile = e.target.aadhar_file.files[0];
  const photo = e.target.photo.files[0];
  
  try {
    if (panFile || aadharFile || photo) {
      // With files - use multiUpload
      const files = {};
      if (panFile) files.pan_file = panFile;
      if (aadharFile) files.aadhar_file = aadharFile;
      if (photo) files.photo = photo;
      
      await api.uploadMultiple(
        '/users/with-files',
        files,
        { user_data: JSON.stringify(userData) }
      );
    } else {
      // Without files - use JSON
      await api.post('/users', userData);
    }
    
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

### Public Holidays Module

The Public Holidays module implements our standardized approach for both JSON data and file uploads:

#### Backend Implementation

```python
# JSON endpoint for creating holidays
@router.post("/")
def create_public_holiday(
    holiday: PublicHoliday = Body(...), 
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Create a new public holiday using JSON.
    Only admins and superadmins can create holidays.
    """
    holiday_id = holiday_service.create_holiday(holiday, current_emp_id, hostname)
    return {"message": "Public holiday created successfully", "id": holiday_id}

# File upload endpoint with /with-file suffix
@router.post("/import/with-file")
async def import_holidays_with_file(
    file: UploadFile = File(...), 
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Import multiple holidays from an Excel file.
    """
    # Validate file type and size
    is_valid, error = validate_file(
        file, 
        allowed_types=["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
        max_size=5*1024*1024
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Process file and import holidays
    contents = await file.read()
    # ...
```

#### Frontend Implementation

```javascript
// PublicHolidays.jsx
const handleAddHoliday = async (holidayData) => {
  try {
    // Using JSON for regular data
    await api.post('/public-holidays/', holidayData);
    // Handle success
  } catch (error) {
    // Handle error
  }
};

const handleImportHolidays = async (file) => {
  try {
    // Using upload for file operations
    await api.upload('/public-holidays/import/with-file', file);
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

### Leave Management Module

The Leave Management module demonstrates JSON data exchange:

#### Backend Implementation

```python
@router.post("/apply", response_model=dict)
def create_leave_application(
    leave: EmployeeLeave = Body(...), 
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Create a new leave application using JSON.
    """
    leave.emp_id = emp_id
    return apply_leave(leave, hostname)

@router.put("/{leave_id}/status", response_model=dict)
def update_leave_application_status(
    leave_id: str,
    status: LeaveStatus = Body(...),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Update the status of a leave application (approve/reject) using JSON.
    """
    return update_leave_status(leave_id, status, emp_id, hostname)
```

#### Frontend Implementation

```javascript
// LeaveManagement.jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  
  // Format dates to YYYY-MM-DD
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const leaveData = {
    leave_name: leaveType,
    start_date: formatDate(startDate),
    end_date: formatDate(endDate),
    reason: reason
  };

  try {
    // Using JSON for leave application
    await api.post('/leaves/apply', leaveData);
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

### Company Leaves Module

The Company Leaves module demonstrates simple JSON data exchange:

#### Backend Implementation

```python
@router.post("/")
def create_leave(
    data: CompanyLeaveCreate = Body(...), 
    role: str = Depends(role_checker(["superadmin", "admin"])), 
    hostname: str = Depends(extract_hostname)
):
    """
    Create a new company leave type using JSON.
    Only accessible by admin or superadmin.
    """
    return company_leave_service.create_leave(data, hostname)

@router.put("/{leave_id}")
def update_leave(
    leave_id: str, 
    data: CompanyLeaveUpdate = Body(...), 
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["superadmin", "admin"]))
):
    """
    Update a company leave type using JSON.
    Only accessible by admin or superadmin.
    """
    # Process and update leave
    return {"message": "Leave updated successfully"}
```

#### Frontend Implementation

```javascript
// CompanyLeaves.jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    if (editingId) {
      // Update existing company leave
      await api.put(`/company-leaves/${editingId}`, formData);
    } else {
      // Create new company leave
      await api.post('/company-leaves', formData);
    }
    // Handle success
  } catch (err) {
    // Handle error
  }
};
```

### Salary Module

The Salary Module implements our standardized approach for both JSON data exchange and file uploads:

#### Backend Implementation

```python
# JSON endpoint for creating salary components
@router.post("/", response_model=SalaryComponentInDB, status_code=status.HTTP_201_CREATED)
def create_component(
    component: SalaryComponentCreate = Body(...),
    hostname: str = Depends(extract_hostname)
):
    """
    Create a new salary component using JSON.
    """
    return create_salary_component(component, hostname)

# JSON endpoint for assigning components to employees
@router.post("/assignments/{emp_id}", status_code=status.HTTP_201_CREATED)
def create_assignments(
    emp_id: str,
    components: List[SalaryComponentAssignment] = Body(...),
    hostname: str = Depends(extract_hostname)
):
    """
    Create salary component assignments for an employee using JSON.
    """
    return create_salary_component_assignments(emp_id, components, hostname)

# File upload endpoint with /with-file suffix
@router.post("/assignments/import/with-file", status_code=status.HTTP_201_CREATED)
async def import_assignments_with_file(
    file: UploadFile = File(...),
    hostname: str = Depends(extract_hostname)
):
    """
    Import salary component assignments from an Excel file.
    """
    # Validate file type and size
    is_valid, error = validate_file(
        file, 
        allowed_types=["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
        max_size=5*1024*1024
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Process file and import assignments
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    assignments_data = df.to_dict('records')
    
    return {"message": "Assignments imported successfully"}
```

#### Frontend Implementation

```javascript
// SalaryComponents.jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const componentData = {
      name: formData.name,
      type: formData.type,
      // Other component fields
    };

    if (editingId) {
      // Using JSON for update
      await api.put(`/salary-components/${editingId}`, componentData);
    } else {
      // Using JSON for create
      await api.post('/salary-components', componentData);
    }
    // Handle success
  } catch (error) {
    // Handle error
  }
};

// SalaryUsersList.jsx
const handleImport = async (e) => {
  e.preventDefault();
  if (!importFile) {
    return; // No file selected
  }

  try {
    // Using upload for file operations
    await api.upload('/salary-components/assignments/import/with-file', importFile);
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

By following these guidelines, we ensure consistent data exchange between frontend and backend components of our application. 