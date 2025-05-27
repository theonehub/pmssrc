# API controllers 

# Import only the new SOLID-compliant controllers that we know work
try:
    from .payout_controller import PayoutController
except ImportError:
    PayoutController = None

try:
    from .payslip_controller import PayslipController
except ImportError:
    PayslipController = None

try:
    from .employee_salary_controller import EmployeeSalaryController
except ImportError:
    EmployeeSalaryController = None

try:
    from .auth_controller import AuthController
except ImportError:
    AuthController = None

__all__ = [
    "PayoutController",
    "PayslipController", 
    "EmployeeSalaryController",
    "AuthController"
] 