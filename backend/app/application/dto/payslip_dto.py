"""
Payslip Application Layer DTOs
Data Transfer Objects for payslip operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import date, datetime
from enum import Enum


class PayslipFormatEnum(str, Enum):
    """Payslip format enumeration"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    EXCEL = "excel"


class PayslipStatusEnum(str, Enum):
    """Payslip status enumeration"""
    PENDING = "pending"
    GENERATING = "generating"
    GENERATED = "generated"
    FAILED = "failed"
    EMAILED = "emailed"
    EMAIL_FAILED = "email_failed"
    DOWNLOADED = "downloaded"
    EXPIRED = "expired"


class BulkOperationTypeEnum(str, Enum):
    """Bulk operation type enumeration"""
    GENERATE = "generate"
    EMAIL = "email"
    DOWNLOAD = "download"


class BulkOperationStatusEnum(str, Enum):
    """Bulk operation status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ==================== REQUEST DTOs ====================

class PayslipGenerationRequestDTO(BaseModel):
    """Request DTO for payslip generation"""
    payout_id: str
    format: PayslipFormatEnum = PayslipFormatEnum.PDF
    template_id: Optional[str] = None
    auto_email: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAY123",
                "format": "pdf",
                "auto_email": True
            }
        }


class PayslipEmailRequestDTO(BaseModel):
    """Request DTO for payslip email"""
    payout_id: str
    recipient_email: Optional[str] = None
    custom_subject: Optional[str] = Field(None, max_length=200)
    custom_message: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAY123",
                "recipient_email": "employee@example.com",
                "custom_subject": "Your Salary Slip for March 2024"
            }
        }


class PayslipHistoryRequestDTO(BaseModel):
    """Request DTO for payslip history"""
    employee_id: str
    year: int
    month: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "year": 2024,
                "month": 3
            }
        }


class BulkPayslipGenerationRequestDTO(BaseModel):
    """Request DTO for bulk payslip generation"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    employee_ids: Optional[List[str]] = None
    department_id: Optional[str] = None
    format: PayslipFormatEnum = PayslipFormatEnum.PDF
    auto_email: bool = False
    template_id: Optional[str] = None
    
    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v > current_year + 1:
            raise ValueError("Year cannot be more than 1 year in the future")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": 3,
                "year": 2024,
                "format": "pdf",
                "auto_email": True
            }
        }


class BulkPayslipEmailRequestDTO(BaseModel):
    """Request DTO for bulk payslip email"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    employee_ids: Optional[List[str]] = None
    department_id: Optional[str] = None
    custom_subject: Optional[str] = Field(None, max_length=200)
    custom_message: Optional[str] = Field(None, max_length=1000)
    include_attachments: bool = True
    
    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v > current_year + 1:
            raise ValueError("Year cannot be more than 1 year in the future")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": 3,
                "year": 2024,
                "custom_subject": "Your Salary Slip for March 2024",
                "include_attachments": True
            }
        }


class PayslipTemplateRequestDTO(BaseModel):
    """Request DTO for payslip template"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    html_content: str
    css_content: Optional[str] = None
    header_html: Optional[str] = None
    footer_html: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Standard Template",
                "description": "Default payslip template",
                "html_content": "<div>Payslip content here</div>",
                "css_content": "body { font-family: Arial; }"
            }
        }


class PayslipScheduleRequestDTO(BaseModel):
    """Request DTO for payslip schedule"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    scheduled_date: datetime
    auto_email: bool = True
    template_id: Optional[str] = None
    
    @validator('scheduled_date')
    def validate_scheduled_date(cls, v):
        if v < datetime.now():
            raise ValueError("Scheduled date cannot be in the past")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": 3,
                "year": 2024,
                "scheduled_date": "2024-03-01T00:00:00Z",
                "auto_email": True
            }
        }


class PayslipSearchFiltersDTO(BaseModel):
    """Request DTO for searching payslips"""
    employee_id: Optional[str] = None
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = None
    status: Optional[PayslipStatusEnum] = None
    format: Optional[PayslipFormatEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "month": 3,
                "year": 2024,
                "status": "generated",
                "format": "pdf",
                "skip": 0,
                "limit": 50
            }
        }


# ==================== RESPONSE DTOs ====================

class PayslipResponseDTO(BaseModel):
    """Response DTO for payslip generation"""
    payout_id: str
    employee_id: str
    status: PayslipStatusEnum
    format: PayslipFormatEnum
    generated_at: datetime
    file_url: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAY123",
                "employee_id": "EMP001",
                "status": "generated",
                "format": "pdf",
                "generated_at": "2024-03-01T12:00:00Z",
                "file_url": "https://example.com/payslips/PAY123.pdf"
            }
        }


class PayslipEmailResponseDTO(BaseModel):
    """Response DTO for payslip email"""
    payout_id: str
    employee_id: str
    sent_at: datetime
    recipient_email: str
    status: str
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAY123",
                "employee_id": "EMP001",
                "sent_at": "2024-03-01T12:00:00Z",
                "recipient_email": "employee@example.com",
                "status": "sent"
            }
        }


class PayslipHistoryResponseDTO(BaseModel):
    """Response DTO for payslip history"""
    employee_id: str
    year: int
    month: Optional[int]
    payslips: List[PayslipResponseDTO]
    total_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "year": 2024,
                "month": 3,
                "payslips": [],
                "total_count": 0
            }
        }


class BulkPayslipOperationResponseDTO(BaseModel):
    """Response DTO for bulk payslip operations"""
    operation_id: str
    operation_type: BulkOperationTypeEnum
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_count: int
    processed_count: int
    success_count: int
    error_count: int
    error_details: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "operation_id": "BULK123",
                "operation_type": "generate",
                "status": "completed",
                "started_at": "2024-03-01T12:00:00Z",
                "completed_at": "2024-03-01T12:05:00Z",
                "total_count": 100,
                "processed_count": 100,
                "success_count": 98,
                "error_count": 2
            }
        }


class PayslipSummaryResponseDTO(BaseModel):
    """Response DTO for payslip summary"""
    year: int
    month: int
    total_payslips: int
    total_generated: int
    total_emailed: int
    total_downloaded: int
    generation_success_rate: float
    email_success_rate: float
    download_rate: float
    average_generation_time: float
    error_count: int
    last_generated: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "month": 3,
                "total_payslips": 100,
                "total_generated": 98,
                "total_emailed": 95,
                "total_downloaded": 80,
                "generation_success_rate": 98.0,
                "email_success_rate": 95.0,
                "download_rate": 80.0,
                "average_generation_time": 2.5,
                "error_count": 2,
                "last_generated": "2024-03-01T12:00:00Z"
            }
        }


class PayslipTemplateResponseDTO(BaseModel):
    """Response DTO for payslip template"""
    template_id: str
    name: str
    description: str
    is_default: bool
    created_at: datetime
    updated_at: datetime
    preview_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "TEMP123",
                "name": "Standard Template",
                "description": "Default payslip template",
                "is_default": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "preview_url": "https://example.com/templates/TEMP123/preview.png"
            }
        }


class PayslipScheduleResponseDTO(BaseModel):
    """Response DTO for payslip schedule"""
    schedule_id: str
    month: int
    year: int
    scheduled_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "schedule_id": "SCH123",
                "month": 3,
                "year": 2024,
                "scheduled_date": "2024-03-01T00:00:00Z",
                "status": "scheduled",
                "created_at": "2024-02-28T12:00:00Z",
                "updated_at": "2024-02-28T12:00:00Z"
            }
        }


class PayslipDownloadResponseDTO(BaseModel):
    """Response DTO for payslip download info"""
    payout_id: str
    employee_id: str
    download_count: int
    last_downloaded: Optional[datetime] = None
    file_url: Optional[str] = None
    expiry_date: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAY123",
                "employee_id": "EMP001",
                "download_count": 2,
                "last_downloaded": "2024-03-01T12:00:00Z",
                "file_url": "https://example.com/payslips/PAY123.pdf",
                "expiry_date": "2024-04-01T00:00:00Z"
            }
        }


class PayslipAnalyticsResponseDTO(BaseModel):
    """Response DTO for payslip analytics"""
    period: str
    total_payslips_generated: int
    total_emails_sent: int
    total_downloads: int
    average_generation_time: float
    most_downloaded_month: Optional[str] = None
    employee_engagement_rate: float
    template_usage_stats: Dict[str, int]
    monthly_trends: List[Dict[str, Any]]
    error_statistics: Dict[str, int]
    generated_at: datetime


# ==================== ERROR DTOs ====================

class PayslipErrorResponseDTO(BaseModel):
    """Response DTO for payslip errors"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    payslip_id: Optional[str] = None
    payout_id: Optional[str] = None
    employee_id: Optional[str] = None


class PayslipSummaryDTO(BaseModel):
    """DTO for payslip summary data"""
    total_payslips: int
    total_generated: int
    total_emailed: int
    total_downloaded: int
    generation_success_rate: float
    email_success_rate: float
    download_rate: float
    average_generation_time: float
    error_count: int
    last_generated: Optional[datetime] = None
    
    @validator('generation_success_rate', 'email_success_rate', 'download_rate')
    def validate_rates(cls, v):
        return round(v, 2)


class PayslipAnalyticsDTO(BaseModel):
    """DTO for payslip analytics data"""
    period: str
    total_payslips: int
    total_generated: int
    total_emailed: int
    total_downloaded: int
    generation_success_rate: float
    email_success_rate: float
    download_rate: float
    average_generation_time: float
    error_count: int
    most_common_errors: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]
    template_usage: Dict[str, int]
    employee_engagement: Dict[str, float]
    
    @validator('generation_success_rate', 'email_success_rate', 'download_rate')
    def validate_rates(cls, v):
        return round(v, 2)


# ==================== ERROR CLASSES ====================

class PayslipValidationError(Exception):
    """Exception raised for payslip validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class PayslipBusinessRuleError(Exception):
    """Exception raised for payslip business rule violations"""
    def __init__(self, message: str, rule_name: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.rule_name = rule_name
        self.details = details or {}
        super().__init__(self.message)


class PayslipNotFoundError(Exception):
    """Exception raised when payslip is not found"""
    def __init__(self, payout_id: str, employee_id: Optional[str] = None):
        self.payout_id = payout_id
        self.employee_id = employee_id
        message = f"Payslip not found for payout {payout_id}"
        if employee_id:
            message += f" and employee {employee_id}"
        super().__init__(message)
