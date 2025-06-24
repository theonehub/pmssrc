"""
Employee Repository Interface
Defines the contract for employee data persistence operations
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date

from app.domain.entities.employee import Employee, EmployeeStatus, EmployeeType
from app.domain.value_objects.employee_id import EmployeeId


class EmployeeRepository(ABC):
    """
    Employee repository interface following SOLID principles.
    
    Follows SOLID principles:
    - SRP: Only defines employee persistence operations
    - OCP: Can be implemented by different storage mechanisms
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for employee operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    def get_by_id(self, employee_id: EmployeeId) -> Optional[Employee]:
        """
        Get employee by ID.
        
        Args:
            employee_id: The employee identifier
            
        Returns:
            Employee entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def save(self, employee: Employee) -> None:
        """
        Save employee entity.
        
        Args:
            employee: The employee entity to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    def delete(self, employee_id: EmployeeId) -> bool:
        """
        Delete employee by ID.
        
        Args:
            employee_id: The employee identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, employee_id: EmployeeId) -> bool:
        """
        Check if employee exists.
        
        Args:
            employee_id: The employee identifier
            
        Returns:
            True if employee exists, False otherwise
        """
        pass


class EmployeeQueryRepository(ABC):
    """
    Separate interface for employee queries following ISP.
    
    This interface is separated from the main repository to follow
    the Interface Segregation Principle - clients that only need
    to query data don't depend on persistence methods.
    """
    
    @abstractmethod
    def get_all_active(self) -> List[Employee]:
        """
        Get all active employees.
        
        Returns:
            List of active employees
        """
        pass
    
    @abstractmethod
    def get_by_status(self, status: EmployeeStatus) -> List[Employee]:
        """
        Get employees by status.
        
        Args:
            status: The employee status to filter by
            
        Returns:
            List of employees with the specified status
        """
        pass
    
    @abstractmethod
    def get_by_department(self, department: str) -> List[Employee]:
        """
        Get employees by department.
        
        Args:
            department: The department name
            
        Returns:
            List of employees in the department
        """
        pass
    
    @abstractmethod
    def get_by_manager(self, manager_id: EmployeeId) -> List[Employee]:
        """
        Get employees by manager.
        
        Args:
            manager_id: The manager's employee ID
            
        Returns:
            List of employees reporting to the manager
        """
        pass
    
    @abstractmethod
    def get_by_employee_type(self, employee_type: EmployeeType) -> List[Employee]:
        """
        Get employees by type.
        
        Args:
            employee_type: The employee type to filter by
            
        Returns:
            List of employees of the specified type
        """
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Employee]:
        """
        Find employee by email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            Employee if found, None otherwise
        """
        pass
    
    @abstractmethod
    def search_by_name(self, name_pattern: str) -> List[Employee]:
        """
        Search employees by name pattern.
        
        Args:
            name_pattern: Pattern to match against employee names
            
        Returns:
            List of employees matching the pattern
        """
        pass
    
    @abstractmethod
    def get_joining_in_date_range(self, start_date: date, end_date: date) -> List[Employee]:
        """
        Get employees who joined within a date range.
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            
        Returns:
            List of employees who joined in the date range
        """
        pass
    
    @abstractmethod
    def get_by_salary_range(self, min_salary: float, max_salary: float) -> List[Employee]:
        """
        Get employees within a salary range.
        
        Args:
            min_salary: Minimum salary amount
            max_salary: Maximum salary amount
            
        Returns:
            List of employees within the salary range
        """
        pass
    
    @abstractmethod
    def count_by_department(self) -> Dict[str, int]:
        """
        Get employee count by department.
        
        Returns:
            Dictionary mapping department names to employee counts
        """
        pass
    
    @abstractmethod
    def count_by_status(self) -> Dict[str, int]:
        """
        Get employee count by status.
        
        Returns:
            Dictionary mapping status values to employee counts
        """
        pass


class EmployeeAnalyticsRepository(ABC):
    """
    Separate interface for employee analytics queries.
    
    This interface provides complex analytical queries that might
    be implemented differently (e.g., using data warehouse, OLAP, etc.)
    """
    
    @abstractmethod
    def get_salary_statistics(self) -> Dict[str, Any]:
        """
        Get salary statistics across all employees.
        
        Returns:
            Dictionary containing salary statistics (avg, min, max, etc.)
        """
        pass
    
    @abstractmethod
    def get_tenure_distribution(self) -> Dict[str, int]:
        """
        Get distribution of employee tenure.
        
        Returns:
            Dictionary mapping tenure ranges to employee counts
        """
        pass
    
    @abstractmethod
    def get_age_distribution(self) -> Dict[str, int]:
        """
        Get distribution of employee ages.
        
        Returns:
            Dictionary mapping age ranges to employee counts
        """
        pass
    
    @abstractmethod
    def get_department_salary_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get salary statistics by department.
        
        Returns:
            Dictionary mapping departments to their salary statistics
        """
        pass
    
    @abstractmethod
    def get_promotion_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Get promotion trends over specified months.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            List of promotion trend data
        """
        pass
    
    @abstractmethod
    def get_attrition_rate(self, months: int = 12) -> float:
        """
        Calculate attrition rate over specified months.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Attrition rate as percentage
        """
        pass


class EmployeeRepositoryError(Exception):
    """Base exception for employee repository operations"""
    pass


class EmployeeNotFoundError(EmployeeRepositoryError):
    """Exception raised when employee is not found"""
    
    def __init__(self, employee_id: EmployeeId):
        self.employee_id = employee_id
        super().__init__(f"Employee not found: {employee_id}")


class EmployeeAlreadyExistsError(EmployeeRepositoryError):
    """Exception raised when trying to create an employee that already exists"""
    
    def __init__(self, employee_id: EmployeeId):
        self.employee_id = employee_id
        super().__init__(f"Employee already exists: {employee_id}")


class EmployeeRepositoryConnectionError(EmployeeRepositoryError):
    """Exception raised when repository connection fails"""
    pass 