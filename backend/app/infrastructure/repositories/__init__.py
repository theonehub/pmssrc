# Repository implementations 

# Import all SOLID repositories
try:
    from .solid_user_repository import SolidUserRepository
    from .solid_payout_repository import SolidPayoutRepository
    from .solid_attendance_repository import SolidAttendanceRepository
    from .solid_employee_leave_repository import SolidEmployeeLeaveRepository
    from .solid_reimbursement_repository import SolidReimbursementRepository
    from .solid_public_holiday_repository import SolidPublicHolidayRepository
    from .solid_company_leave_repository import SolidCompanyLeaveRepository
    from .solid_organisation_repository import SolidOrganisationRepository
    from .solid_reimbursement_assignment_repository import SolidReimbursementAssignmentRepository
    from .solid_reimbursement_types_repository import SolidReimbursementTypesRepository
    from .solid_activity_tracker_repository import SolidActivityTrackerRepository
    from .solid_salary_history_repository import SolidSalaryHistoryRepository
    
    __all__ = [
        "SolidUserRepository", 
        "SolidPayoutRepository", 
        "SolidAttendanceRepository", 
        "SolidEmployeeLeaveRepository", 
        "SolidReimbursementRepository",
        "SolidPublicHolidayRepository",
        "SolidCompanyLeaveRepository",
        "SolidOrganisationRepository",
        "SolidReimbursementAssignmentRepository",
        "SolidReimbursementTypesRepository",
        "SolidActivityTrackerRepository",
        "SolidSalaryHistoryRepository"
    ]
except ImportError as e:
    # Fallback if imports fail
    __all__ = [] 