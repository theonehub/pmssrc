"""
Payslip Data Transfer Objects
DTOs for payslip generation, emailing, and management operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PayslipFormat(str, Enum):
    """Payslip format options."""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"


class PayslipFormatEnum(str, Enum):
    """Payslip format options (alias for compatibility)."""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"


class PayslipStatus(str, Enum):
    """Payslip status options."""
    PENDING = "pending"
    GENERATING = "generating"
    GENERATED = "generated"
    FAILED = "failed"
    SENT = "sent"
    DOWNLOADED = "downloaded"


class PayslipStatusEnum(str, Enum):
    """Payslip status options (alias for compatibility)."""
    PENDING = "pending"
    GENERATING = "generating"
    GENERATED = "generated"
    FAILED = "failed"
    SENT = "sent"
    DOWNLOADED = "downloaded"


class EmailStatus(str, Enum):
    """Email status options."""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"


class OperationStatus(str, Enum):
    """Bulk operation status options."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BulkOperationTypeEnum(str, Enum):
    """Bulk operation type options."""
    GENERATE = "generate"
    EMAIL = "email"
    DOWNLOAD = "download"


# Request DTOs
class PayslipGenerationRequestDTO(BaseModel):
    """Request DTO for generating individual payslip."""
    payout_id: str = Field(..., description="Unique payout identifier")
    format: PayslipFormat = Field(PayslipFormat.PDF, description="Output format")
    include_tax_details: bool = Field(True, description="Include tax calculation details")
    include_deductions: bool = Field(True, description="Include deduction breakdown")
    custom_message: Optional[str] = Field(None, description="Custom message for payslip")
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAYOUT_EMP001_202401",
                "format": "pdf",
                "include_tax_details": True,
                "include_deductions": True,
                "custom_message": "Thank you for your hard work!"
            }
        }


class PayslipEmailRequestDTO(BaseModel):
    """Request DTO for emailing payslip."""
    payout_id: str = Field(..., description="Unique payout identifier")
    recipient_email: Optional[str] = Field(None, description="Recipient email (defaults to employee email)")
    cc_emails: Optional[List[str]] = Field(None, description="CC email addresses")
    subject: Optional[str] = Field(None, description="Custom email subject")
    message: Optional[str] = Field(None, description="Custom email message")
    attach_pdf: bool = Field(True, description="Attach PDF payslip")
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAYOUT_EMP001_202401",
                "recipient_email": "employee@company.com",
                "cc_emails": ["hr@company.com"],
                "subject": "Your Payslip for January 2024",
                "message": "Please find your payslip attached.",
                "attach_pdf": True
            }
        }


class PayslipHistoryRequestDTO(BaseModel):
    """Request DTO for getting payslip history."""
    employee_id: str = Field(..., description="Employee identifier")
    year: Optional[int] = Field(None, description="Year filter")
    month: Optional[int] = Field(None, description="Month filter (1-12)")
    status: Optional[PayslipStatus] = Field(None, description="Status filter")
    format: Optional[PayslipFormat] = Field(None, description="Format filter")
    limit: int = Field(50, ge=1, le=100, description="Maximum records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")
    
    @validator('month')
    def validate_month(cls, v):
        if v is not None and (v < 1 or v > 12):
            raise ValueError('Month must be between 1 and 12')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "year": 2024,
                "month": 1,
                "status": "generated",
                "limit": 20,
                "offset": 0
            }
        }


class BulkPayslipGenerationRequestDTO(BaseModel):
    """Request DTO for bulk payslip generation."""
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2030, description="Year")
    employee_ids: Optional[List[str]] = Field(None, description="Specific employee IDs (if not provided, all employees)")
    format: PayslipFormat = Field(PayslipFormat.PDF, description="Output format")
    include_tax_details: bool = Field(True, description="Include tax calculation details")
    include_deductions: bool = Field(True, description="Include deduction breakdown")
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": 1,
                "year": 2024,
                "employee_ids": ["EMP001", "EMP002"],
                "format": "pdf",
                "include_tax_details": True,
                "include_deductions": True
            }
        }


class BulkPayslipEmailRequestDTO(BaseModel):
    """Request DTO for bulk payslip emailing."""
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2030, description="Year")
    employee_ids: Optional[List[str]] = Field(None, description="Specific employee IDs")
    cc_emails: Optional[List[str]] = Field(None, description="CC email addresses")
    subject_template: Optional[str] = Field(None, description="Email subject template")
    message_template: Optional[str] = Field(None, description="Email message template")
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": 1,
                "year": 2024,
                "employee_ids": ["EMP001", "EMP002"],
                "cc_emails": ["hr@company.com"],
                "subject_template": "Your Payslip for {month} {year}",
                "message_template": "Dear {employee_name}, please find your payslip attached."
            }
        }


class PayslipTemplateRequestDTO(BaseModel):
    """Request DTO for payslip template operations."""
    template_name: str = Field(..., description="Template name")
    template_data: Dict[str, Any] = Field(..., description="Template configuration")
    is_default: bool = Field(False, description="Set as default template")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_name": "Standard Template",
                "template_data": {
                    "header_color": "#003366",
                    "include_logo": True,
                    "footer_text": "Company Confidential"
                },
                "is_default": True
            }
        }


class PayslipScheduleRequestDTO(BaseModel):
    """Request DTO for payslip schedule creation."""
    schedule_name: str = Field(..., description="Schedule name")
    cron_expression: str = Field(..., description="Cron expression for schedule")
    auto_generate: bool = Field(True, description="Auto-generate payslips")
    auto_email: bool = Field(False, description="Auto-email payslips")
    template_id: Optional[str] = Field(None, description="Template to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "schedule_name": "Monthly Payslips",
                "cron_expression": "0 9 1 * *",
                "auto_generate": True,
                "auto_email": True,
                "template_id": "TEMPLATE_001"
            }
        }


# Response DTOs
class PayslipResponseDTO(BaseModel):
    """Response DTO for individual payslip."""
    payslip_id: str = Field(..., description="Unique payslip identifier")
    payout_id: str = Field(..., description="Associated payout identifier")
    employee_id: str = Field(..., description="Employee identifier")
    format: PayslipFormat = Field(..., description="Payslip format")
    status: PayslipStatus = Field(..., description="Payslip status")
    generated_at: Optional[datetime] = Field(None, description="Generation timestamp")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    download_count: int = Field(0, description="Number of times downloaded")
    last_downloaded: Optional[datetime] = Field(None, description="Last download timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "payslip_id": "PAYSLIP_EMP001_202401",
                "payout_id": "PAYOUT_EMP001_202401",
                "employee_id": "EMP001",
                "format": "pdf",
                "status": "generated",
                "generated_at": "2024-01-31T10:00:00Z",
                "file_size": 1024,
                "download_count": 2,
                "last_downloaded": "2024-02-01T09:00:00Z"
            }
        }


class PayslipEmailResponseDTO(BaseModel):
    """Response DTO for payslip email operation."""
    payslip_id: str = Field(..., description="Payslip identifier")
    payout_id: str = Field(..., description="Payout identifier")
    employee_id: str = Field(..., description="Employee identifier")
    recipient_email: str = Field(..., description="Recipient email address")
    email_status: EmailStatus = Field(..., description="Email delivery status")
    sent_at: Optional[datetime] = Field(None, description="Email sent timestamp")
    delivery_confirmed_at: Optional[datetime] = Field(None, description="Delivery confirmation timestamp")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "payslip_id": "PAYSLIP_EMP001_202401",
                "payout_id": "PAYOUT_EMP001_202401",
                "employee_id": "EMP001",
                "recipient_email": "employee@company.com",
                "email_status": "sent",
                "sent_at": "2024-01-31T10:15:00Z",
                "message": "Payslip emailed successfully"
            }
        }


class PayslipHistoryResponseDTO(BaseModel):
    """Response DTO for payslip history."""
    employee_id: str = Field(..., description="Employee identifier")
    year: Optional[int] = Field(None, description="Filtered year")
    month: Optional[int] = Field(None, description="Filtered month")
    total_payslips: int = Field(..., description="Total number of payslips")
    payslips: List[PayslipResponseDTO] = Field(..., description="List of payslips")
    download_statistics: Dict[str, Any] = Field(..., description="Download statistics")
    last_generated: Optional[datetime] = Field(None, description="Last payslip generation date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "year": 2024,
                "total_payslips": 12,
                "payslips": [],
                "download_statistics": {
                    "total_downloads": 24,
                    "average_downloads_per_payslip": 2.0
                },
                "last_generated": "2024-01-31T10:00:00Z"
            }
        }


class BulkPayslipOperationResponseDTO(BaseModel):
    """Response DTO for bulk payslip operations."""
    operation_id: str = Field(..., description="Unique operation identifier")
    operation_type: str = Field(..., description="Type of operation (generate/email)")
    status: OperationStatus = Field(..., description="Operation status")
    month: int = Field(..., description="Target month")
    year: int = Field(..., description="Target year")
    total_employees: int = Field(..., description="Total employees to process")
    processed_count: int = Field(0, description="Number of employees processed")
    successful_count: int = Field(0, description="Number of successful operations")
    failed_count: int = Field(0, description="Number of failed operations")
    successful_operations: List[str] = Field(default_factory=list, description="List of successful employee IDs")
    failed_operations: List[Dict[str, str]] = Field(default_factory=list, description="List of failed operations with reasons")
    started_at: Optional[datetime] = Field(None, description="Operation start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Operation completion timestamp")
    processing_duration: Optional[float] = Field(None, description="Processing duration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "operation_id": "BULK_GEN_01_2024_1704096000",
                "operation_type": "generate",
                "status": "completed",
                "month": 1,
                "year": 2024,
                "total_employees": 100,
                "processed_count": 100,
                "successful_count": 98,
                "failed_count": 2,
                "successful_operations": ["EMP001", "EMP002"],
                "failed_operations": [
                    {"employee_id": "EMP003", "reason": "Missing payout data"}
                ],
                "started_at": "2024-01-31T09:00:00Z",
                "completed_at": "2024-01-31T09:15:00Z",
                "processing_duration": 900.0
            }
        }


class PayslipSummaryResponseDTO(BaseModel):
    """Response DTO for monthly payslip summary."""
    month: int = Field(..., description="Summary month")
    year: int = Field(..., description="Summary year")
    total_employees: int = Field(..., description="Total employees")
    generated_payslips: int = Field(..., description="Number of generated payslips")
    emailed_payslips: int = Field(..., description="Number of emailed payslips")
    downloaded_payslips: int = Field(..., description="Number of downloaded payslips")
    pending_payslips: int = Field(..., description="Number of pending payslips")
    failed_payslips: int = Field(..., description="Number of failed payslips")
    generation_statistics: Dict[str, Any] = Field(..., description="Generation statistics")
    email_statistics: Dict[str, Any] = Field(..., description="Email statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": 1,
                "year": 2024,
                "total_employees": 100,
                "generated_payslips": 98,
                "emailed_payslips": 95,
                "downloaded_payslips": 90,
                "pending_payslips": 2,
                "failed_payslips": 0,
                "generation_statistics": {
                    "success_rate": 98.0,
                    "average_generation_time": 2.5
                },
                "email_statistics": {
                    "delivery_rate": 97.0,
                    "bounce_rate": 2.0
                }
            }
        }


class PayslipTemplateResponseDTO(BaseModel):
    """Response DTO for payslip template."""
    template_id: str = Field(..., description="Template identifier")
    template_name: str = Field(..., description="Template name")
    template_data: Dict[str, Any] = Field(..., description="Template configuration")
    is_default: bool = Field(..., description="Is default template")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "TEMPLATE_001",
                "template_name": "Standard Template",
                "template_data": {
                    "header_color": "#003366",
                    "include_logo": True
                },
                "is_default": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        }


class PayslipScheduleResponseDTO(BaseModel):
    """Response DTO for payslip schedule."""
    schedule_id: str = Field(..., description="Schedule identifier")
    schedule_name: str = Field(..., description="Schedule name")
    cron_expression: str = Field(..., description="Cron expression")
    auto_generate: bool = Field(..., description="Auto-generate enabled")
    auto_email: bool = Field(..., description="Auto-email enabled")
    template_id: Optional[str] = Field(None, description="Associated template ID")
    is_active: bool = Field(..., description="Schedule is active")
    last_run: Optional[datetime] = Field(None, description="Last execution timestamp")
    next_run: Optional[datetime] = Field(None, description="Next scheduled execution")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "schedule_id": "SCHEDULE_001",
                "schedule_name": "Monthly Payslips",
                "cron_expression": "0 9 1 * *",
                "auto_generate": True,
                "auto_email": True,
                "template_id": "TEMPLATE_001",
                "is_active": True,
                "last_run": "2024-01-01T09:00:00Z",
                "next_run": "2024-02-01T09:00:00Z",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class PayslipDownloadResponseDTO(BaseModel):
    """Response DTO for payslip download information."""
    payslip_id: str = Field(..., description="Payslip identifier")
    payout_id: str = Field(..., description="Payout identifier")
    employee_id: str = Field(..., description="Employee identifier")
    file_name: str = Field(..., description="Download file name")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME content type")
    download_url: str = Field(..., description="Download URL")
    expires_at: datetime = Field(..., description="URL expiration timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "payslip_id": "PAYSLIP_EMP001_202401",
                "payout_id": "PAYOUT_EMP001_202401",
                "employee_id": "EMP001",
                "file_name": "payslip_EMP001_Jan2024.pdf",
                "file_size": 1024,
                "content_type": "application/pdf",
                "download_url": "https://api.company.com/payslips/download/xyz123",
                "expires_at": "2024-02-01T23:59:59Z"
            }
        }


class PayslipAnalyticsResponseDTO(BaseModel):
    """Response DTO for payslip analytics."""
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")
    total_payslips_generated: int = Field(..., description="Total payslips generated")
    total_emails_sent: int = Field(..., description="Total emails sent")
    total_downloads: int = Field(..., description="Total downloads")
    generation_trends: Dict[str, Any] = Field(..., description="Generation trends")
    email_delivery_stats: Dict[str, Any] = Field(..., description="Email delivery statistics")
    employee_engagement_stats: Dict[str, Any] = Field(..., description="Employee engagement statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "period_start": "2024-01-01T00:00:00Z",
                "period_end": "2024-01-31T23:59:59Z",
                "total_payslips_generated": 100,
                "total_emails_sent": 95,
                "total_downloads": 90,
                "generation_trends": {
                    "daily_average": 3.2,
                    "peak_day": "2024-01-31"
                },
                "email_delivery_stats": {
                    "success_rate": 95.0,
                    "bounce_rate": 2.0
                },
                "employee_engagement_stats": {
                    "download_rate": 90.0,
                    "average_days_to_download": 2.5
                }
            }
        }


class PayslipErrorResponseDTO(BaseModel):
    """Response DTO for payslip errors."""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")


# Additional DTOs required by routes
class PayslipSearchFiltersDTO(BaseModel):
    """DTO for payslip search filters."""
    employee_id: Optional[str] = Field(None, description="Employee ID filter")
    year: Optional[int] = Field(None, description="Year filter")
    month: Optional[int] = Field(None, description="Month filter")
    status: Optional[PayslipStatus] = Field(None, description="Status filter")
    format: Optional[PayslipFormat] = Field(None, description="Format filter")


class PayslipSummaryDTO(BaseModel):
    """DTO for payslip summary information."""
    total_payslips: int = Field(..., description="Total number of payslips")
    generated_count: int = Field(..., description="Number of generated payslips")
    emailed_count: int = Field(..., description="Number of emailed payslips")
    downloaded_count: int = Field(..., description="Number of downloaded payslips")
    failed_count: int = Field(..., description="Number of failed payslips")


class PayslipAnalyticsDTO(BaseModel):
    """DTO for payslip analytics data."""
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")
    total_operations: int = Field(..., description="Total operations")
    success_rate: float = Field(..., description="Success rate percentage")
    average_processing_time: float = Field(..., description="Average processing time in seconds")


# Exception DTOs (used for error responses)
class PayslipValidationError(Exception):
    """Exception for payslip validation errors."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class PayslipBusinessRuleError(Exception):
    """Exception for payslip business rule violations."""
    def __init__(self, message: str, rule: Optional[str] = None):
        self.message = message
        self.rule = rule
        super().__init__(message)


class PayslipNotFoundError(Exception):
    """Exception for when payslip is not found."""
    def __init__(self, payslip_id: str):
        self.payslip_id = payslip_id
        super().__init__(f"Payslip not found: {payslip_id}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "PAYSLIP_GENERATION_FAILED",
                "error_message": "Failed to generate payslip due to missing payout data",
                "error_details": {
                    "payout_id": "PAYOUT_EMP001_202401",
                    "missing_fields": ["basic_salary", "deductions"]
                },
                "timestamp": "2024-01-31T10:00:00Z",
                "request_id": "REQ_12345"
            }
        } 