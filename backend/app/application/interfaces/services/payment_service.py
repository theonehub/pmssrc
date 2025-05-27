"""
Payment Service Interface
Defines the contract for payment operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal


class PaymentService(ABC):
    """
    Payment service interface following SOLID principles.
    
    Follows SOLID principles:
    - SRP: Only defines payment operations
    - OCP: Can be implemented by different payment providers
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for payment operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    def process_payment(
        self,
        payment_id: str,
        recipient_account: str,
        amount: Decimal,
        currency: str = "INR",
        payment_method: str = "bank_transfer",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a payment to a recipient.
        
        Args:
            payment_id: Unique payment identifier
            recipient_account: Recipient's account details
            amount: Payment amount
            currency: Currency code (default: INR)
            payment_method: Payment method (bank_transfer, upi, etc.)
            description: Payment description
            metadata: Additional payment metadata
            
        Returns:
            Payment result with status and transaction details
        """
        pass
    
    @abstractmethod
    def process_bulk_payments(
        self,
        payments: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Process multiple payments in bulk.
        
        Args:
            payments: List of payment dictionaries
            
        Returns:
            Dictionary mapping payment IDs to their results
        """
        pass
    
    @abstractmethod
    def get_payment_status(
        self,
        payment_id: str
    ) -> Dict[str, Any]:
        """
        Get the status of a payment.
        
        Args:
            payment_id: Payment identifier
            
        Returns:
            Payment status information
        """
        pass
    
    @abstractmethod
    def cancel_payment(
        self,
        payment_id: str,
        reason: str
    ) -> bool:
        """
        Cancel a pending payment.
        
        Args:
            payment_id: Payment identifier
            reason: Cancellation reason
            
        Returns:
            True if cancellation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_account(
        self,
        account_details: Dict[str, str]
    ) -> bool:
        """
        Validate recipient account details.
        
        Args:
            account_details: Account information to validate
            
        Returns:
            True if account is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_payment_history(
        self,
        start_date: date,
        end_date: date,
        status_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get payment history for a date range.
        
        Args:
            start_date: Start date for history
            end_date: End date for history
            status_filter: Filter by payment status
            limit: Maximum number of records
            
        Returns:
            List of payment records
        """
        pass
    
    @abstractmethod
    def calculate_fees(
        self,
        amount: Decimal,
        payment_method: str,
        currency: str = "INR"
    ) -> Decimal:
        """
        Calculate payment processing fees.
        
        Args:
            amount: Payment amount
            payment_method: Payment method
            currency: Currency code
            
        Returns:
            Calculated fee amount
        """
        pass
    
    @abstractmethod
    def get_supported_payment_methods(self) -> List[str]:
        """
        Get list of supported payment methods.
        
        Returns:
            List of supported payment method codes
        """
        pass
    
    @abstractmethod
    def verify_payment(
        self,
        payment_id: str,
        verification_code: Optional[str] = None
    ) -> bool:
        """
        Verify a payment transaction.
        
        Args:
            payment_id: Payment identifier
            verification_code: Optional verification code
            
        Returns:
            True if payment is verified, False otherwise
        """
        pass


class PaymentServiceError(Exception):
    """Base exception for payment service operations"""
    pass


class PaymentProcessingError(PaymentServiceError):
    """Exception raised when payment processing fails"""
    
    def __init__(self, payment_id: str, reason: str):
        self.payment_id = payment_id
        self.reason = reason
        super().__init__(f"Payment processing failed for {payment_id}: {reason}")


class PaymentValidationError(PaymentServiceError):
    """Exception raised when payment validation fails"""
    
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Payment validation error for {field}: {reason}")


class PaymentConfigurationError(PaymentServiceError):
    """Exception raised when payment service is misconfigured"""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Payment service configuration error: {reason}")


class InsufficientFundsError(PaymentServiceError):
    """Exception raised when there are insufficient funds"""
    
    def __init__(self, available_amount: Decimal, requested_amount: Decimal):
        self.available_amount = available_amount
        self.requested_amount = requested_amount
        super().__init__(f"Insufficient funds: available {available_amount}, requested {requested_amount}")


class PaymentNotFoundError(PaymentServiceError):
    """Exception raised when payment is not found"""
    
    def __init__(self, payment_id: str):
        self.payment_id = payment_id
        super().__init__(f"Payment not found: {payment_id}") 