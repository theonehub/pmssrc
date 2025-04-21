# Project Functionality Overview

This document provides a detailed overview of the functionalities implemented in the project, based on the provided file list. It covers both frontend and backend aspects, focusing on user-facing features and their interactions with backend services.

## User Authentication and Authorization

### User Registration and Login

- **Functionality:** Allows users to register new accounts and log in with existing credentials.
- **Implementation:**
    - **Frontend:** The `frontend/src/Components/Auth/Login.jsx` component handles user login. It likely sends a request to the backend with user credentials.
    - **Backend:**
        - `backend/app/auth/auth.py` likely contains the logic for user authentication, verifying credentials against stored user data.
        - `backend/app/routes/auth_routes.py` probably defines the API endpoints for login and registration, which call the authentication logic in `auth.py`.
        
### Test Cases

- **Test Case:** Test user registration
  - **Description:** Verify that a new user can register successfully.
  - **Steps:**
    1. Navigate to the registration page.
    2. Enter valid user details (name, username, password, etc.).
    3. Submit the registration form.
    4. Check if the registration is successful and the user is redirected to the login page or receives a success message.
  - **Expected Result:** The user should be registered successfully and redirected to the login page or receive a success message.

        - `backend/app/models/user_model.py` defines the structure of the user data stored in the database.
        - Password handling is likely managed in `backend/app/auth/password_handler.py` (hashing, verification).
        - `backend/app/auth/jwt_handler.py` likely handles JSON Web Token (JWT) creation and verification for maintaining user sessions.

### Role-Based Access Control

- **Functionality:** Restricts access to certain features based on user roles (e.g., admin, employee).
- **Implementation:**
    - **Frontend:** `frontend/src/Components/Common/ProtectedRoute.jsx` likely handles route protection based on user roles, redirecting unauthorized users.
    - **Backend:**
        - Role checks are likely implemented in the route handlers (e.g., in `backend/app/routes`), using the JWT payload to identify the user's role and authorize access to specific resources.
        - `backend/app/auth/dependencies.py` might define dependencies for checking user roles before allowing access to certain routes.
        - The `user_model.py` might include a `role` attribute.

### Password Management

- **Functionality:** Allows users to reset or update their passwords.
- **Implementation:**
    - Password reset functionality details are not clear from the file list, but it would likely involve:
        - **Frontend:** A password reset form and logic to send a reset request.
        - **Backend:** An endpoint in `auth_routes.py` to handle the reset request, potentially involving sending an email with a reset token, validating the token, and updating the password in the database.  `password_handler.py` would handle the password hashing.
    - Password update:
        - **Frontend:** User profile or settings page to update password.
        - **Backend:** An endpoint in `user_routes.py` to handle password updates, using `password_handler.py` to hash the new password.

## Leave Management

### Applying for Leaves

- **Functionality:** Allows users to submit leave requests.
- **Implementation:**
    - **Frontend:**  The file list suggests components for leave management, such as `frontend/src/Components/Leaves/AllLeaves.jsx` and potentially components within.  These would provide UI elements for selecting leave dates, types, and submitting requests.
    - **Backend:**
        - `backend/app/routes/leave_routes.py` likely defines API endpoints for creating leave requests.
        - `backend/app/services/employee_leave_service.py` probably contains the business logic for handling leave requests, interacting with the database.
        - `backend/app/models/leave_model.py` defines the structure of leave requests (dates, type, status, user ID, etc.).

### Approving/Rejecting Leave Requests

- **Functionality:** Allows authorized users (e.g., managers) to approve or reject leave requests.
- **Implementation:**
    - **Frontend:** Components involved in leave management (mentioned above) might include functionality for approving/rejecting requests, possibly restricted by user role.
    - **Backend:**
        - `backend/app/routes/leave_routes.py` would have endpoints for updating the status of leave requests.
        - `backend/app/services/employee_leave_service.py` handles the logic for updating leave request statuses in the database.
        - Role-based access control would be enforced to ensure only authorized users can perform these actions.

### Viewing Leave Balances

- **Functionality:** Allows users to view their available leave balances.
- **Implementation:**
    - **Frontend:** Leave management components would display leave balance information, likely fetched from the backend.
    - **Backend:**
        - `backend/app/routes/leave_routes.py` or `backend/app/routes/user_routes.py` could have an endpoint to retrieve a user's leave balance.
        - `backend/app/services/employee_leave_service.py` or `backend/app/services/user_service.py` would contain the logic for calculating and retrieving leave balances, possibly considering leave policies, accruals, and taken leaves.

### Company Leave Management

- **Functionality:**  Managing company-wide leave policies or allowances.
- **Implementation:**
    - **Frontend:**  `frontend/src/Components/CompanyLeaves/CompanyLeaves.jsx` likely provides an interface for managing company leave.
    - **Backend:**
        - `backend/app/routes/company_leave_routes.py` defines endpoints for managing company leave.
        - `backend/app/services/company_leave_service.py` handles the logic for interacting with company leave data.
        - `backend/app/models/company_leave.py` defines the data structure for company leave information.

## Attendance Tracking

### Recording Daily Attendance

- **Functionality:** Allows users to record their daily attendance (e.g., check-in/check-out).
- **Implementation:**
    - **Frontend:**  The `frontend/src/Components/Attendence/AttendanceCalendar.jsx` or another attendance-related component would provide the UI for recording attendance.
    - **Backend:**
        - `backend/app/routes/attendance_routes.py` likely defines an endpoint for submitting attendance records.
        - `backend/app/services/attendance_service.py` handles the logic for saving attendance data to the database.
        - `backend/app/models/attendance.py` defines the structure of attendance records (user ID, date, time, etc.).

### Viewing Attendance History

- **Functionality:** Allows users to view their past attendance records.
- **Implementation:**
    - **Frontend:**  The `AttendanceCalendar.jsx` or a related component would display attendance history, fetched from the backend.
    - **Backend:**
        - `backend/app/routes/attendance_routes.py` would have an endpoint to retrieve attendance history for a user.
        - `backend/app/services/attendance_service.py` would handle the data retrieval logic.

### Managing Attendance Records

- **Functionality:**  Potentially allows authorized users to manage or correct attendance records.  The extent of this functionality is unclear from the file names.
- **Implementation:**  Similar to recording and viewing, but with role-based access control and potentially endpoints for updating or correcting records.

## Public Holiday Management

### Viewing Public Holiday Lists

- **Functionality:** Displays a list of public holidays.
- **Implementation:**
    - **Frontend:** `frontend/src/Components/PublicHolidays/PublicHolidays.jsx` likely displays the list of public holidays.
    - **Backend:**
        - `backend/app/routes/public_holiday_routes.py` has an endpoint to retrieve the list of public holidays.
        - `backend/app/services/public_holiday_service.py` handles the data retrieval.
        - `backend/app/models/public_holiday.py` defines the structure of public holiday data.

### Adding/Removing Public Holidays

- **Functionality:** Allows authorized users to add or remove public holidays.
- **Implementation:**
    - **Frontend:** `PublicHolidays.jsx` along with `AddHolidayDialog.jsx` would provide the UI for adding and removing holidays.
    - **Backend:**
        - `backend/app/routes/public_holiday_routes.py` would have endpoints for creating and deleting holidays.
        - `backend/app/services/public_holiday_service.py` handles the data modification logic.
        - Role-based access control would be enforced.

### Importing Public Holidays

- **Functionality:** Allows importing public holidays, possibly from a file or external source.
- **Implementation:**
    - **Frontend:** `ImportHolidaysDialog.jsx` suggests a dialog for importing holidays.
    - **Backend:**
        - `backend/app/routes/public_holiday_routes.py` would have an endpoint to handle the import process.
        - `backend/app/services/public_holiday_service.py` would contain the import logic, potentially parsing data from a file and saving it to the database.

## Reimbursement Management

### Applying for Reimbursements

- **Functionality:** Allows users to submit reimbursement requests.
- **Implementation:**
    - **Frontend:**  `frontend/src/Components/Reimbursements/MyReimbursements.jsx` or related components likely handle reimbursement requests.
    - **Backend:**
        - `backend/app/routes/reimbursements.py` defines endpoints for creating reimbursement requests.
        - `backend/app/services/reimbursements.py` handles the logic for saving requests.
        - `backend/app/models/reimbursements.py` defines the data structure for reimbursement requests.

### Approving/Rejecting Reimbursement Requests

- **Functionality:** Allows authorized users to approve or reject reimbursement requests.
- **Implementation:**
    - **Frontend:** Components for managing reimbursements might include functionality for approval/rejection, with role-based restrictions.
    - **Backend:**
        - `backend/app/routes/reimbursements.py` would have endpoints for updating the status of requests.
        - `backend/app/services/reimbursements.py` handles the logic for updating statuses.

### Managing Reimbursement Types

- **Functionality:** Managing different types of reimbursements (e.g., travel, food, accommodation).
- **Implementation:**
    - **Frontend:**  `frontend/src/Components/Reimbursements/ReimbursementTypes.jsx` likely provides an interface for this.
    - **Backend:**
        - `backend/app/routes/reimbursement_type_routes.py` handles requests related to reimbursement types.
        - `backend/app/services/reimbursement_type_service.py` contains the business logic.
        - `backend/app/models/reimbursement_type.py` defines the structure for reimbursement types.

### Assigning Reimbursements

- **Functionality:** Possibly assigning specific reimbursement budgets or allowances to employees.
- **Implementation:**
    - **Frontend:** Components like  `AssignReimbursement.jsx`, `AssignReimbursementModal.jsx` and `ReimbursementAssignmentList.jsx` suggest functionality for assigning and managing reimbursements.
    - **Backend:**
        - `backend/app/routes/reimbursement_assignment_route.py` likely handles assignment-related requests.
        - `backend/app/services/reimbursement_assignment_service.py` contains the logic.
        - `backend/app/models/reimbursement_assignment.py` defines the assignment data structure.

## Salary Management

### Managing Salary Components

- **Functionality:** Managing different components of a salary (e.g., base salary, allowances, deductions).
- **Implementation:**
    - **Frontend:**  `frontend/src/Components/Salary/SalaryComponents.jsx` probably provides the interface.
    - **Backend:**
        - `backend/app/routes/salary_component_routes.py` handles requests for salary components.
        - `backend/app/services/salary_component_service.py` contains the logic.
        - `backend/app/models/salary_component.py` defines the data structure.

### Declaring Salary Structures

- **Functionality:** Defining salary structures or templates, likely combining different salary components.
- **Implementation:**
    - **Frontend:**  `frontend/src/Components/Salary/DeclareSalary.jsx` likely handles this.
    - **Backend:**
        - `backend/app/routes/salary_declaration_routes.py` manages requests related to salary declarations.
        - `backend/app/services/salary_declaration_service.py` contains the business logic.
        - `backend/app/models/salary_declaration.py` defines the data structure.

### Assigning Salaries to Employees

- **Functionality:** Assigning a specific salary structure or individual salary components to an employee.
- **Implementation:**
    - **Frontend:** `frontend/src/Components/Salary/AssignSalary.jsx` suggests this functionality.
    - **Backend:**
        - `backend/app/routes/employee_salary_routes.py` likely handles requests for assigning salaries.
        - `backend/app/services/employee_salary_service.py` manages the assignment logic.
        - `backend/app/models/employee_salary.py` defines how employee salaries are stored.

### Viewing Assigned Salary Details

- **Functionality:** Allows users (employees or admins) to view details of assigned salaries.
- **Implementation:**
    - **Frontend:**  `frontend/src/Components/Salary/ViewAssignedSalary.jsx` likely displays this information.
    - **Backend:** Endpoints in `employee_salary_routes.py` or potentially `user_routes.py` to fetch salary details.

## User Management

### Managing User Profiles

- **Functionality:**  Potentially allows users to update their profile information. The extent of this is unclear from the file names.
- **Implementation:**
    - **Frontend:**  Likely a profile or settings page, not explicitly named in the list.
    - **Backend:** `backend/app/routes/user_routes.py` would have endpoints for updating user information.  `backend/app/services/user_service.py` would handle the logic, and `backend/app/models/user_model.py` defines the data structure.

### Listing Users

- **Functionality:** Allows authorized users (e.g., admins) to view a list of users.
- **Implementation:**
    - **Frontend:** `frontend/src/Components/User/UsersList.jsx` likely displays the user list.
    - **Backend:**
        - `backend/app/routes/user_routes.py` has an endpoint to retrieve the user list.
        - `backend/app/services/user_service.py` handles the data retrieval.

## Project Attributes

### Managing Project-Related Attributes

- **Functionality:** Managing attributes related to projects (e.g., project names, descriptions, teams).
- **Implementation:**
    - **Frontend:**  `frontend/src/features/project-attributes/components/ProjectAttributes.jsx` handles this.
    - **Backend:**
        - `backend/app/routes/project_attributes_routes.py` manages requests related to project attributes.
        - `backend/app/services/project_attributes_service.py` contains the business logic.
        - `backend/app/models/project_attributes.py` defines the data structure.

## LWP Management

### Functionalities Related to LWP (Leave Without Pay)

- **Functionality:** Managing Leave Without Pay requests or policies.
- **Implementation:**
    - **Frontend:**  `frontend/src/features/lwp/components/LWPManagement.jsx` likely handles this.  Since LWP is a type of leave, it might also interact with the general leave management components.
    - **Backend:**  While not explicitly clear, LWP functionalities might be integrated with the existing leave management routes, services, and models, or have dedicated routes/services if the logic is significantly different. There might be specific handling in `backend/app/services/employee_leave_service.py` or potentially separate files if LWP has unique requirements.

## Limitations and Known Issues

A thorough analysis of the code within each file would be necessary to identify specific limitations or known issues.  This overview is based on file names and structure, providing a general understanding of the implemented functionalities.