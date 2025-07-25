# User Routes V2 - Detailed API Documentation

## Overview
This document provides a comprehensive analysis of the `user_routes_v2.py` file, detailing each endpoint with their complete data structures, input parameters, and response formats. The API follows RESTful principles and implements clean architecture with SOLID principles.

## Base URL
All endpoints are prefixed with `/v2/users`

---

## 1. Department and Designation Endpoints

### 1.1 GET `/v2/users/departments`
**Purpose**: Get list of all departments in the organisation

**Authentication**: Required (CurrentUser)

**Input Parameters**: None

**Response Structure**:
```json
{
  "departments": ["string[]"],
  "organisation": "string",
  "count": "integer"
}
```

**Response Attributes**:
- `departments`: Array of department names
- `organisation`: Current organisation hostname
- `count`: Total number of departments

**Error Responses**:
- `500`: Internal server error with error details

---

### 1.2 GET `/v2/users/designations`
**Purpose**: Get list of all designations in the organisation

**Authentication**: Required (CurrentUser)

**Input Parameters**: None

**Response Structure**:
```json
{
  "designations": ["string[]"],
  "organisation": "string",
  "count": "integer"
}
```

**Response Attributes**:
- `designations`: Array of designation names
- `organisation`: Current organisation hostname
- `count`: Total number of designations

**Error Responses**:
- `500`: Internal server error with error details

---

## 2. Export Endpoints

### 2.1 GET `/v2/users/export`
**Purpose**: Export users to CSV/Excel file

**Authentication**: Required (CurrentUser)

**Query Parameters**:
- `format` (string, optional, default: "csv"): Export format - "csv" or "xlsx"
- `include_inactive` (boolean, optional, default: false): Include inactive users
- `include_deleted` (boolean, optional, default: false): Include deleted users
- `department` (string, optional): Filter by department
- `role` (string, optional): Filter by role

**Response**: File download (CSV or Excel)

**Content Types**:
- CSV: `text/csv`
- Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Error Responses**:
- `500`: Failed to export users

---

## 3. User Query Endpoints

### 3.1 GET `/v2/users/me`
**Purpose**: Get current user's profile

**Authentication**: Required (CurrentUser)

**Input Parameters**: None

**Response Structure**:
```json
{
  "employee_id": "string",
  "name": "string",
  "email": "string",
  "department": "string",
  "designation": "string",
  "role": "string",
  "organisation": "string",
  "last_login": "string (ISO datetime)",
  "permissions": "object"
}
```

**Response Attributes**:
- `employee_id`: Unique employee identifier
- `name`: Full name of the user
- `email`: Email address
- `department`: User's department
- `designation`: User's designation
- `role`: User's role (admin, user, etc.)
- `organisation`: Current organisation hostname
- `last_login`: Last login timestamp
- `permissions`: User's permission object

**Error Responses**:
- `404`: User not found
- `500`: Internal server error

---

### 3.2 GET `/v2/users/my/directs`
**Purpose**: Get direct reports for current user

**Authentication**: Required (CurrentUser)

**Input Parameters**: None

**Response Structure**:
```json
[
  {
    "employee_id": "string",
    "name": "string",
    "email": "string",
    "department": "string",
    "designation": "string",
    "date_of_joining": "string (ISO datetime)",
    "status": "string",
    "organisation": "string"
  }
]
```

**Response Attributes** (per direct report):
- `employee_id`: Unique employee identifier
- `name`: Full name of the direct report
- `email`: Email address
- `department`: Department name
- `designation`: Designation name
- `date_of_joining`: Joining date in ISO format
- `status`: Current status (active, inactive, etc.)
- `organisation`: Organisation hostname

**Error Responses**:
- `500`: Internal server error

---

### 3.3 GET `/v2/users/manager/directs`
**Purpose**: Get direct reports for a specific manager

**Authentication**: Required (CurrentUser)

**Query Parameters**:
- `manager_id` (string, required): Manager's employee ID

**Response Structure**:
```json
[
  {
    "employee_id": "string",
    "name": "string",
    "email": "string",
    "department": "string",
    "designation": "string",
    "manager_id": "string",
    "date_of_joining": "string (ISO datetime)",
    "status": "string",
    "organisation": "string"
  }
]
```

**Response Attributes** (per direct report):
- `employee_id`: Unique employee identifier
- `name`: Full name of the direct report
- `email`: Email address
- `department`: Department name
- `designation`: Designation name
- `manager_id`: Manager's employee ID
- `date_of_joining`: Joining date in ISO format
- `status`: Current status
- `organisation`: Organisation hostname

**Error Responses**:
- `500`: Internal server error

---

### 3.4 GET `/v2/users/stats`
**Purpose**: Get user statistics

**Authentication**: Required (CurrentUser)

**Input Parameters**: None

**Response Structure**:
```json
{
  "total_users": "integer",
  "active_users": "integer",
  "inactive_users": "integer",
  "departments": "object",
  "roles": "object",
  "recent_joiners": "integer",
  "organisation": "string",
  "generated_at": "string (ISO datetime)"
}
```

**Response Attributes**:
- `total_users`: Total number of users
- `active_users`: Number of active users
- `inactive_users`: Number of inactive users
- `departments`: Object with department-wise user counts
- `roles`: Object with role-wise user counts
- `recent_joiners`: Number of recent joiners (TODO: implementation)
- `organisation`: Organisation hostname
- `generated_at`: Timestamp when stats were generated

**Error Responses**:
- `500`: Internal server error

---

### 3.5 GET `/v2/users/template`
**Purpose**: Download user import template with headers

**Authentication**: Required (CurrentUser)

**Query Parameters**:
- `format` (string, optional, default: "csv"): Template format - "csv" or "xlsx"

**Response**: File download (CSV or Excel template)

**Error Responses**:
- `400`: Invalid format (must be 'csv' or 'xlsx')
- `500`: Failed to generate template

---

### 3.6 GET `/v2/users/{employee_id}`
**Purpose**: Get user by ID with complete details

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Response**: UserResponseDTO (nested structure)

**Response Structure** (UserResponseDTO):
```json
{
  "employee_id": "string",
  "name": "string",
  "email": "string",
  "status": "string",
  "personal_details": {
    "gender": "string",
    "date_of_birth": "string (ISO date)",
    "date_of_joining": "string (ISO date)",
    "mobile": "string",
    "date_of_leaving": "string (ISO date)",
    "pan_number": "string",
    "aadhar_number": "string",
    "uan_number": "string",
    "esi_number": "string",
    "formatted_mobile": "string",
    "masked_pan": "string",
    "masked_aadhar": "string"
  },
  "department": "string",
  "designation": "string",
  "location": "string",
  "manager_id": "string",
  "permissions": {
    "role": "string",
    "custom_permissions": ["string[]"],
    "resource_permissions": "object",
    "can_manage_users": "boolean",
    "can_view_reports": "boolean",
    "can_approve_requests": "boolean",
    "is_admin": "boolean",
    "is_superadmin": "boolean"
  },
  "photo_path": "string",
  "pan_document_path": "string",
  "aadhar_document_path": "string",
  "bank_details": {
    "account_number": "string",
    "bank_name": "string",
    "ifsc_code": "string",
    "account_holder_name": "string",
    "branch_name": "string",
    "account_type": "string",
    "masked_account_number": "string",
    "formatted_account_number": "string",
    "bank_code": "string",
    "branch_code": "string",
    "is_valid_for_payment": "boolean"
  },
  "leave_balance": "object",
  "created_at": "string (ISO datetime)",
  "updated_at": "string (ISO datetime)",
  "created_by": "string",
  "updated_by": "string",
  "last_login_at": "string (ISO datetime)",
  "is_active": "boolean",
  "is_locked": "boolean",
  "can_login": "boolean",
  "profile_completion_percentage": "float",
  "display_name": "string",
  "role_display": "string",
  "status_display": "string"
}
```

**Error Responses**:
- `404`: User not found
- `500`: Failed to get user

---

### 3.7 GET `/v2/users/email/{email}`
**Purpose**: Get user by email address

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `email` (string, required): Email address

**Response**: UserResponseDTO (same structure as above)

**Error Responses**:
- `404`: User not found
- `500`: Internal server error

---

### 3.8 POST `/v2/users/search`
**Purpose**: Search users with advanced filters

**Authentication**: Required (CurrentUser)

**Request Body**: UserSearchFiltersDTO

**Request Structure**:
```json
{
  "name": "string (optional)",
  "email": "string (optional)",
  "role": "string (optional)",
  "status": "string (optional)",
  "department": "string (optional)",
  "designation": "string (optional)",
  "location": "string (optional)",
  "manager_id": "string (optional)",
  "gender": "string (optional)",
  "joined_after": "string (ISO datetime, optional)",
  "joined_before": "string (ISO datetime, optional)",
  "created_after": "string (ISO datetime, optional)",
  "created_before": "string (ISO datetime, optional)",
  "is_active": "boolean (optional)",
  "is_locked": "boolean (optional)",
  "has_complete_profile": "boolean (optional)",
  "page": "integer (default: 1)",
  "page_size": "integer (default: 20)",
  "sort_by": "string (default: 'name')",
  "sort_order": "string (default: 'asc')"
}
```

**Response**: UserListResponseDTO

**Response Structure**:
```json
{
  "users": [
    {
      "employee_id": "string",
      "name": "string",
      "email": "string",
      "role": "string",
      "status": "string",
      "mobile": "string",
      "gender": "string",
      "department": "string",
      "designation": "string",
      "date_of_joining": "string (ISO date)",
      "date_of_leaving": "string (ISO date)",
      "last_login_at": "string (ISO datetime)",
      "created_at": "string (ISO datetime)",
      "is_active": "boolean",
      "is_locked": "boolean",
      "profile_completion_percentage": "float"
    }
  ],
  "total_count": "integer",
  "page": "integer",
  "page_size": "integer",
  "total_pages": "integer",
  "has_next": "boolean",
  "has_previous": "boolean"
}
```

**Error Responses**:
- `400`: Invalid search filters
- `500`: Internal server error

---

## 4. User Update Endpoints

### 4.1 PUT `/v2/users/{employee_id}`
**Purpose**: Update user information

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UpdateUserRequestDTO

**Request Structure**:
```json
{
  "name": "string (optional)",
  "email": "string (optional)",
  "gender": "string (optional)",
  "date_of_birth": "string (ISO date, optional)",
  "date_of_joining": "string (ISO date, optional)",
  "date_of_leaving": "string (ISO date, optional)",
  "mobile": "string (optional)",
  "pan_number": "string (optional)",
  "aadhar_number": "string (optional)",
  "uan_number": "string (optional)",
  "esi_number": "string (optional)",
  "department": "string (optional)",
  "designation": "string (optional)",
  "location": "string (optional)",
  "manager_id": "string (optional)",
  "account_number": "string (optional)",
  "bank_name": "string (optional)",
  "ifsc_code": "string (optional)",
  "account_holder_name": "string (optional)",
  "branch_name": "string (optional)",
  "account_type": "string (optional)",
  "updated_by": "string (optional)"
}
```

**Response Structure** (flattened user data):
```json
{
  "employee_id": "string",
  "name": "string",
  "email": "string",
  "department": "string",
  "designation": "string",
  "role": "string",
  "date_of_joining": "string (ISO date)",
  "date_of_birth": "string (ISO date)",
  "gender": "string",
  "mobile": "string",
  "status": "string",
  "manager_id": "string",
  "address": "string",
  "emergency_contact": "string",
  "blood_group": "string",
  "location": "string",
  "pan_number": "string",
  "aadhar_number": "string",
  "uan_number": "string",
  "esi_number": "string",
  "pan_document_path": "string",
  "aadhar_document_path": "string",
  "photo_path": "string",
  "organisation": "string",
  "created_at": "string (ISO datetime)",
  "updated_at": "string (ISO datetime)",
  "is_active": "boolean",
  "last_login_at": "string (ISO datetime)",
  "account_number": "string",
  "bank_name": "string",
  "ifsc_code": "string",
  "account_holder_name": "string",
  "branch_name": "string",
  "account_type": "string"
}
```

**Error Responses**:
- `404`: User not found
- `500`: Failed to update user

---

### 4.2 PATCH `/v2/users/{employee_id}/password`
**Purpose**: Change user password

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: ChangeUserPasswordRequestDTO

**Request Structure**:
```json
{
  "new_password": "string",
  "confirm_password": "string",
  "current_password": "string (optional)",
  "is_admin_reset": "boolean (default: false)",
  "changed_by": "string (optional)"
}
```

**Response**: UserResponseDTO

**Error Responses**:
- `400`: Invalid password data
- `404`: User not found
- `500`: Internal server error

---

### 4.3 PATCH `/v2/users/{employee_id}/role`
**Purpose**: Change user role

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: ChangeUserRoleRequestDTO

**Request Structure**:
```json
{
  "new_role": "string",
  "reason": "string",
  "changed_by": "string (optional)"
}
```

**Response**: UserResponseDTO

**Error Responses**:
- `400`: Invalid role data
- `404`: User not found
- `500`: Internal server error

---

### 4.4 PATCH `/v2/users/{employee_id}/status`
**Purpose**: Update user status (activate, deactivate, suspend, etc.)

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Request Body**: UserStatusUpdateRequestDTO

**Request Structure**:
```json
{
  "status": "string",
  "reason": "string (optional)",
  "suspension_duration_hours": "integer (optional)",
  "updated_by": "string (optional)"
}
```

**Valid Status Values**:
- `active`: Activate user
- `inactive`: Deactivate user
- `suspended`: Suspend user temporarily
- `locked`: Lock user account

**Response**: UserResponseDTO

**Error Responses**:
- `400`: Invalid status data
- `404`: User not found
- `500`: Internal server error

---

### 4.5 DELETE `/v2/users/{employee_id}`
**Purpose**: Delete/deactivate a user

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Response Structure**:
```json
{
  "success": "boolean",
  "message": "string",
  "employee_id": "string",
  "organisation": "string",
  "deleted_at": "string (ISO datetime)",
  "deleted_by": "string"
}
```

**Response Attributes**:
- `success`: Operation success status
- `message`: Success message
- `employee_id`: Deleted user's ID
- `organisation`: Organisation hostname
- `deleted_at`: Deletion timestamp
- `deleted_by`: User who performed deletion

**Error Responses**:
- `500`: Failed to delete user

---

## 5. User Existence and Validation Endpoints

### 5.1 GET `/v2/users/check/exists`
**Purpose**: Check if user exists with given email, mobile, or PAN

**Authentication**: Required (CurrentUser)

**Query Parameters**:
- `email` (string, optional): Email to check
- `mobile` (string, optional): Mobile number to check
- `pan_number` (string, optional): PAN number to check
- `exclude_id` (string, optional): User ID to exclude from check

**Response Structure**:
```json
{
  "email_exists": "boolean",
  "mobile_exists": "boolean",
  "pan_exists": "boolean"
}
```

**Response Attributes**:
- `email_exists`: Whether email already exists
- `mobile_exists`: Whether mobile number already exists
- `pan_exists`: Whether PAN number already exists

**Error Responses**:
- `500`: Internal server error

---

## 6. Import/Export Endpoints

### 6.1 POST `/v2/users/import`
**Purpose**: Import users from CSV/Excel file

**Authentication**: Required (CurrentUser)

**Request Body**: multipart/form-data

**Form Fields**:
- `file` (UploadFile, required): CSV/Excel file containing user data

**Allowed File Types**:
- `.csv`
- `.xlsx`
- `.xls`

**Response Structure**:
```json
{
  "success": "boolean",
  "message": "string",
  "imported_count": "integer",
  "errors": ["string[]"],
  "organisation": "string",
  "imported_at": "string (ISO datetime)",
  "imported_by": "string"
}
```

**Response Attributes**:
- `success`: Import success status
- `message`: Success message
- `imported_count`: Number of users imported
- `errors`: Array of import errors
- `organisation`: Organisation hostname
- `imported_at`: Import timestamp
- `imported_by`: User who performed import

**Error Responses**:
- `400`: No file provided or invalid file type
- `500`: Failed to import users

---

### 6.2 GET `/v2/users/export` (Duplicate)
**Purpose**: Export users to CSV/Excel file (duplicate endpoint)

**Authentication**: Required (CurrentUser)

**Query Parameters**:
- `format` (string, optional, default: "csv"): Export format
- `include_inactive` (boolean, optional, default: false): Include inactive users
- `include_deleted` (boolean, optional, default: false): Include deleted users
- `department` (string, optional): Filter by department
- `role` (string, optional): Filter by role

**Response**: File download

**Error Responses**:
- `400`: Invalid format
- `500`: Failed to export users

---

## 7. User Attendance and Leaves Summary Endpoints

### 7.1 GET `/v2/users/{employee_id}/attendance/summary`
**Purpose**: Get user attendance summary for a specific month

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Query Parameters**:
- `month` (integer, required, 1-12): Month number
- `year` (integer, required, ≥2020): Year

**Response Structure**:
```json
{
  "employee_id": "string",
  "month": "integer",
  "year": "integer",
  "total_working_days": "integer",
  "present_days": "integer",
  "absent_days": "integer",
  "half_days": "integer",
  "late_arrivals": "integer",
  "early_departures": "integer",
  "overtime_hours": "float",
  "attendance_percentage": "float",
  "organisation": "string"
}
```

**Response Attributes**:
- `employee_id`: Employee ID
- `month`: Month number (1-12)
- `year`: Year
- `total_working_days`: Total working days in month
- `present_days`: Days present
- `absent_days`: Days absent
- `half_days`: Half days
- `late_arrivals`: Number of late arrivals
- `early_departures`: Number of early departures
- `overtime_hours`: Total overtime hours
- `attendance_percentage`: Attendance percentage
- `organisation`: Organisation hostname

**Error Responses**:
- `500`: Internal server error

---

### 7.2 GET `/v2/users/{employee_id}/leaves/summary`
**Purpose**: Get user leaves summary for a specific year

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `employee_id` (string, required): Employee ID

**Query Parameters**:
- `year` (integer, required, ≥2020): Year

**Response Structure**:
```json
{
  "employee_id": "string",
  "year": "integer",
  "total_casual_leaves": "integer",
  "used_casual_leaves": "integer",
  "remaining_casual_leaves": "integer",
  "total_sick_leaves": "integer",
  "used_sick_leaves": "integer",
  "remaining_sick_leaves": "integer",
  "total_earned_leaves": "integer",
  "used_earned_leaves": "integer",
  "remaining_earned_leaves": "integer",
  "pending_leave_requests": "integer",
  "organisation": "string"
}
```

**Response Attributes**:
- `employee_id`: Employee ID
- `year`: Year
- `total_casual_leaves`: Total casual leaves allocated
- `used_casual_leaves`: Used casual leaves
- `remaining_casual_leaves`: Remaining casual leaves
- `total_sick_leaves`: Total sick leaves allocated
- `used_sick_leaves`: Used sick leaves
- `remaining_sick_leaves`: Remaining sick leaves
- `total_earned_leaves`: Total earned leaves allocated
- `used_earned_leaves`: Used earned leaves
- `remaining_earned_leaves`: Remaining earned leaves
- `pending_leave_requests`: Number of pending leave requests
- `organisation`: Organisation hostname

**Error Responses**:
- `500`: Internal server error

---

## 8. Profile Picture and Documents Endpoints

### 8.1 GET `/v2/users/{user_id}/profile-picture`
**Purpose**: Get user profile picture

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `user_id` (string, required): User ID

**Response**: File response (image/*)

**Error Responses**:
- `404`: User not found or profile picture not found
- `500`: Internal server error

---

### 8.2 POST `/v2/users/{user_id}/profile-picture`
**Purpose**: Upload user profile picture

**Authentication**: Required (CurrentUser)

**Path Parameters**:
- `user_id` (string, required): User ID

**Request Body**: multipart/form-data

**Form Fields**:
- `photo` (UploadFile, required): User profile picture

**Response Structure**:
```json
{
  "success": "boolean",
  "message": "string",
  "profile_picture_url": "string",
  "user_id": "string",
  "organisation": "string",
  "uploaded_at": "string (ISO datetime)",
  "uploaded_by": "string"
}
```

**Response Attributes**:
- `success`: Upload success status
- `message`: Success message
- `profile_picture_url`: URL to uploaded picture
- `user_id`: User ID
- `organisation`: Organisation hostname
- `uploaded_at`: Upload timestamp
- `uploaded_by`: User who performed upload

**Error Responses**:
- `400`: File must be an image
- `404`: User not found
- `500`: Failed to upload profile picture

---

## 9. Analytics Endpoints

### 9.1 GET `/v2/users/analytics/statistics`
**Purpose**: Get comprehensive user analytics and statistics

**Authentication**: Required (CurrentUser)

**Input Parameters**: None

**Response**: UserStatisticsDTO

**Response Structure**:
```json
{
  "total_users": "integer",
  "active_users": "integer",
  "inactive_users": "integer",
  "suspended_users": "integer",
  "locked_users": "integer",
  "users_by_role": "object",
  "users_by_department": "object",
  "users_by_location": "object",
  "users_with_complete_profiles": "integer",
  "average_profile_completion": "float",
  "users_logged_in_today": "integer",
  "users_logged_in_this_week": "integer",
  "users_logged_in_this_month": "integer",
  "users_created_this_month": "integer",
  "users_created_this_year": "integer"
}
```

**Response Attributes**:
- `total_users`: Total number of users
- `active_users`: Number of active users
- `inactive_users`: Number of inactive users
- `suspended_users`: Number of suspended users
- `locked_users`: Number of locked users
- `users_by_role`: Object with role-wise user counts
- `users_by_department`: Object with department-wise user counts
- `users_by_location`: Object with location-wise user counts
- `users_with_complete_profiles`: Number of users with complete profiles
- `average_profile_completion`: Average profile completion percentage
- `users_logged_in_today`: Users logged in today
- `users_logged_in_this_week`: Users logged in this week
- `users_logged_in_this_month`: Users logged in this month
- `users_created_this_month`: Users created this month
- `users_created_this_year`: Users created this year

**Error Responses**:
- `500`: Internal server error

---

## 10. User Management Endpoints

### 10.1 GET `/v2/users`
**Purpose**: Get a paginated list of users with optional filters

**Authentication**: Required (CurrentUser)

**Query Parameters**:
- `skip` (integer, optional, default: 0, ≥0): Number of records to skip
- `limit` (integer, optional, default: 10, 1-1000): Number of records to return
- `include_inactive` (boolean, optional, default: false): Include inactive users
- `include_deleted` (boolean, optional, default: false): Include deleted users
- `search` (string, optional): Search query for users
- `department` (string, optional): Filter by department
- `role` (string, optional): Filter by role
- `manager_id` (string, optional): Filter by manager ID
- `designation` (string, optional): Filter by designation
- `location` (string, optional): Filter by location

**Response Structure**:
```json
{
  "total": "integer",
  "users": ["UserSummaryDTO[]"],
  "page": "integer",
  "page_size": "integer",
  "total_pages": "integer",
  "has_next": "boolean",
  "has_previous": "boolean"
}
```

**Response Attributes**:
- `total`: Total number of users
- `users`: Array of user summary objects
- `page`: Current page number
- `page_size`: Page size
- `total_pages`: Total number of pages
- `has_next`: Whether there's a next page
- `has_previous`: Whether there's a previous page

**Error Responses**:
- `500`: Failed to fetch users

---

### 10.2 POST `/v2/users/create`
**Purpose**: Create a new user (JSON body, no files)

**Authentication**: Required (CurrentUser)

**Request Body**: CreateUserRequestDTO

**Request Structure**:
```json
{
  "employee_id": "string",
  "name": "string",
  "email": "string",
  "password": "string",
  "gender": "string",
  "date_of_birth": "string (ISO date)",
  "date_of_joining": "string (ISO date)",
  "mobile": "string",
  "date_of_leaving": "string (ISO date, optional)",
  "role": "string (default: 'user')",
  "pan_number": "string (optional)",
  "aadhar_number": "string (optional)",
  "uan_number": "string (optional)",
  "esi_number": "string (optional)",
  "department": "string (optional)",
  "designation": "string (optional)",
  "location": "string (optional)",
  "manager_id": "string (optional)",
  "photo_path": "string (optional)",
  "pan_document_path": "string (optional)",
  "aadhar_document_path": "string (optional)",
  "account_number": "string (optional)",
  "bank_name": "string (optional)",
  "ifsc_code": "string (optional)",
  "account_holder_name": "string (optional)",
  "branch_name": "string (optional)",
  "account_type": "string (optional)",
  "created_by": "string (optional)"
}
```

**Response**: UserResponseDTO

**Error Responses**:
- `400`: Invalid user data
- `409`: User already exists
- `500`: Internal server error

---

### 10.3 POST `/v2/users/create-with-files`
**Purpose**: Create a new user with file uploads (multipart/form-data)

**Authentication**: Required (CurrentUser)

**Request Body**: multipart/form-data

**Form Fields**:
- `user_data` (string, required): User data as JSON string
- `pan_file` (UploadFile, optional): PAN document
- `aadhar_file` (UploadFile, optional): Aadhar document
- `photo` (UploadFile, optional): Profile photo

**Response**: UserResponseDTO

**Error Responses**:
- `400`: Invalid user data or file format
- `409`: User already exists
- `500`: Internal server error

---

## 11. Duplicate Endpoints

The following endpoints appear twice in the file and serve the same purpose:

1. **PUT `/v2/users/{employee_id}`** - Update user (appears twice)
2. **PATCH `/v2/users/{employee_id}/password`** - Change password (appears twice)
3. **PATCH `/v2/users/{employee_id}/role`** - Change role (appears twice)
4. **PATCH `/v2/users/{employee_id}/status`** - Update status (appears twice)
5. **DELETE `/v2/users/{employee_id}`** - Delete user (appears twice)
6. **GET `/v2/users/export`** - Export users (appears twice)

## 12. Data Transfer Objects (DTOs) Summary

### Request DTOs:
1. **CreateUserRequestDTO**: For creating new users
2. **UpdateUserRequestDTO**: For updating user information
3. **UpdateUserDocumentsRequestDTO**: For updating user documents
4. **ChangeUserPasswordRequestDTO**: For changing user passwords
5. **ChangeUserRoleRequestDTO**: For changing user roles
6. **UserStatusUpdateRequestDTO**: For updating user status
7. **UserSearchFiltersDTO**: For advanced user search
8. **UserLoginRequestDTO**: For user login

### Response DTOs:
1. **UserResponseDTO**: Complete user information
2. **UserSummaryDTO**: User summary for lists
3. **UserListResponseDTO**: Paginated user list
4. **UserStatisticsDTO**: User statistics
5. **UserAnalyticsDTO**: User analytics
6. **UserLoginResponseDTO**: Login response
7. **PersonalDetailsResponseDTO**: Personal details
8. **UserDocumentsResponseDTO**: User documents
9. **BankDetailsResponseDTO**: Bank details
10. **UserPermissionsResponseDTO**: User permissions

## 13. Error Handling

All endpoints follow consistent error handling patterns:

- **400 Bad Request**: Invalid input data
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **500 Internal Server Error**: Server-side errors

## 14. Authentication and Authorization

All endpoints require authentication via `CurrentUser` dependency. The system uses organisation-based segregation where users can only access data within their organisation.

## 15. File Upload Support

The API supports file uploads for:
- Profile pictures
- PAN documents
- Aadhar documents
- User import files (CSV/Excel)

## 16. Pagination

List endpoints support pagination with:
- `skip`: Number of records to skip
- `limit`: Number of records to return
- `page`: Page number
- `page_size`: Page size

## 17. Search and Filtering

Advanced search and filtering capabilities include:
- Text search across multiple fields
- Department, role, and status filtering
- Date range filtering
- Manager-based filtering
- Location-based filtering

This comprehensive API provides complete user management functionality with proper validation, error handling, and organisation-based data segregation. 