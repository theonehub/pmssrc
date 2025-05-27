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
    GENERATED = "generated"
    EMAILED = "emailed"
    DOWNLOADED = "downloaded"
    FAILED = "failed"


class BulkOperationTypeEnum(str, Enum):
    """Bulk operation type enumeration"""
    GENERATE = "generate"
    EMAIL = "email"


class BulkOperationStatusEnum(str, Enum):
    """Bulk operation status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


# ==================== REQUEST DTOs ====================

class PayslipGenerationRequestDTO(BaseModel):
    """Request DTO for payslip generation"""
    payout_id: str = Field(..., min_length=1, max_length=100)
    format: PayslipFormatEnum = PayslipFormatEnum.PDF
    include_company_logo: bool = True
    custom_template_id: Optional[str] = None
    custom_filename: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAYOUT_123",
                "format": "pdf",
                "include_company_logo": True,
                "custom_template_id": "template_001"
            }
        }


class PayslipEmailRequestDTO(BaseModel):
    """Request DTO for payslip email"""
    payout_id: str = Field(..., min_length=1, max_length=100)
    recipient_email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    custom_subject: Optional[str] = Field(None, max_length=200)
    custom_message: Optional[str] = Field(None, max_length=1000)
    include_attachments: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAYOUT_123",
                "recipient_email": "employee@company.com",
                "custom_subject": "Your Salary Slip for March 2024",
                "custom_message": "Please find your salary slip attached."
            }
        }


class PayslipHistoryRequestDTO(BaseModel):
    """Request DTO for payslip history"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=2020, le=2030)
    month: Optional[int] = Field(None, ge=1, le=12)
    status_filter: Optional[PayslipStatusEnum] = None
    
    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v > current_year + 1:
            raise ValueError("Year cannot be more than 1 year in the future")
        return v


class BulkPayslipGenerationRequestDTO(BaseModel):
    """Request DTO for bulk payslip generation"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    employee_ids: Optional[List[str]] = Field(None, description="Specific employees (if None, all employees)")
    format: PayslipFormatEnum = PayslipFormatEnum.PDF
    status_filter: Optional[str] = Field(None, description="Filter payouts by status")
    template_id: Optional[str] = None
    auto_email: bool = False
    
    @validator('employee_ids')
    def validate_employee_ids(cls, v):
        if v is not None:
            if len(v) == 0:
                raise ValueError("Employee IDs list cannot be empty")
            if len(set(v)) != len(v):
                raise ValueError("Duplicate employee IDs found")
        return v


class BulkPayslipEmailRequestDTO(BaseModel):
    """Request DTO for bulk payslip email"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    employee_ids: Optional[List[str]] = Field(None, description="Specific employees (if None, all employees)")
    custom_subject: Optional[str] = Field(None, max_length=200)
    custom_message: Optional[str] = Field(None, max_length=1000)
    send_copy_to_admin: bool = False
    
    @validator('employee_ids')
    def validate_employee_ids(cls, v):
        if v is not None:
            if len(v) == 0:
                raise ValueError("Employee IDs list cannot be empty")
            if len(set(v)) != len(v):
                raise ValueError("Duplicate employee IDs found")
        return v


class PayslipTemplateRequestDTO(BaseModel):
    """Request DTO for payslip template operations"""
    template_name: str = Field(..., min_length=1, max_length=100)
    template_content: Optional[str] = None
    is_default: bool = False
    description: Optional[str] = Field(None, max_length=500)


class PayslipScheduleRequestDTO(BaseModel):
    """Request DTO for payslip schedule operations"""
    day_of_month: int = Field(..., ge=1, le=28, description="Day of month to generate payslips")
    auto_email: bool = False
    template_id: Optional[str] = None
    enabled: bool = True


# ==================== RESPONSE DTOs ====================

class PayslipResponseDTO(BaseModel):
    """Response DTO for payslip data"""
    payslip_id: str
    payout_id: str
    employee_id: str
    employee_name: Optional[str] = None
    format: PayslipFormatEnum
    status: PayslipStatusEnum
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    generated_at: datetime
    generated_by: Optional[str] = None
    email_sent_at: Optional[datetime] = None
    email_recipient: Optional[str] = None
    download_count: int = 0
    last_downloaded_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "payslip_id": "PAYSLIP_123",
                "payout_id": "PAYOUT_123",
                "employee_id": "EMP001",
                "employee_name": "John Doe",
                "format": "pdf",
                "status": "generated",
                "file_size": 102400,
                "generated_at": "2024-03-15T10:30:00",
                "download_count": 2
            }
        }


class PayslipEmailResponseDTO(BaseModel):
    """Response DTO for payslip email operations"""
    payslip_id: str
    payout_id: str
    employee_id: str
    recipient_email: str
    email_status: str
    sent_at: datetime
    message: str
    error_details: Optional[str] = None


class PayslipHistoryResponseDTO(BaseModel):
    """Response DTO for payslip history"""
    employee_id: str
    employee_name: Optional[str] = None
    year: int
    month: Optional[int] = None
    total_payslips: int
    payslips: List[PayslipResponseDTO]
    download_statistics: Dict[str, int]  # {"total_downloads": 10, "unique_months": 5}
    last_generated: Optional[datetime] = None


class BulkPayslipOperationResponseDTO(BaseModel):
    """Response DTO for bulk payslip operations"""
    operation_id: str
    operation_type: BulkOperationTypeEnum
    status: BulkOperationStatusEnum
    month: int
    year: int
    total_employees: int
    processed_count: int
    successful_count: int
    failed_count: int
    successful_operations: List[str]  # List of payslip IDs or email addresses
    failed_operations: List[Dict[str, str]]  # List of {employee_id, error}
    started_at: datetime
    completed_at: Optional[datetime] = None
    processing_duration: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "operation_id": "BULK_OP_123",
                "operation_type": "generate",
                "status": "completed",
                "month": 3,
                "year": 2024,
                "total_employees": 50,
                "successful_count": 48,
                "failed_count": 2,
                "processing_duration": 125.5
            }
        }


class PayslipSummaryResponseDTO(BaseModel):
    """Response DTO for payslip summary"""
    month: int
    year: int
    total_employees: int
    payslips_generated: int
    payslips_emailed: int
    payslips_downloaded: int
    pending_generation: int
    failed_generation: int
    generation_rate: float  # percentage
    email_delivery_rate: float  # percentage
    download_rate: float  # percentage
    last_generated_at: Optional[datetime] = None
    
    @validator('generation_rate', 'email_delivery_rate', 'download_rate')
    def validate_rates(cls, v):
        return round(v, 2)


class PayslipTemplateResponseDTO(BaseModel):
    """Response DTO for payslip templates"""
    template_id: str
    template_name: str
    description: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    usage_count: int = 0


class PayslipScheduleResponseDTO(BaseModel):
    """Response DTO for payslip schedules"""
    schedule_id: str
    day_of_month: int
    auto_email: bool
    template_id: Optional[str] = None
    template_name: Optional[str] = None
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_executed_at: Optional[datetime] = None
    next_execution_date: Optional[date] = None


class PayslipDownloadResponseDTO(BaseModel):
    """Response DTO for payslip download operations"""
    payslip_id: str
    payout_id: str
    employee_id: str
    filename: str
    file_size: int
    content_type: str
    download_token: Optional[str] = None
    expires_at: Optional[datetime] = None


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
