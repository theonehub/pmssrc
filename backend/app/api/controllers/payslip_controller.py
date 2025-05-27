"""
SOLID-Compliant Payslip Controller
Handles HTTP requests for payslip operations
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from io import BytesIO

from app.application.dto.payslip_dto import (
    PayslipGenerationRequestDTO, PayslipEmailRequestDTO, PayslipHistoryRequestDTO,
    BulkPayslipGenerationRequestDTO, BulkPayslipEmailRequestDTO, PayslipTemplateRequestDTO,
    PayslipScheduleRequestDTO, PayslipResponseDTO, PayslipEmailResponseDTO,
    PayslipHistoryResponseDTO, BulkPayslipOperationResponseDTO, PayslipSummaryResponseDTO,
    PayslipTemplateResponseDTO, PayslipScheduleResponseDTO, PayslipDownloadResponseDTO,
    PayslipAnalyticsResponseDTO, PayslipErrorResponseDTO
)

logger = logging.getLogger(__name__)


class PayslipController:
    """
    SOLID-compliant controller for payslip operations.
    
    Responsibilities:
    - Handle HTTP request/response mapping for payslip operations
    - Validate input data
    - Coordinate with payslip business services
    - Return standardized responses
    """
    
    def __init__(self):
        """Initialize payslip controller."""
        pass
    
    async def health_check(self) -> Dict[str, str]:
        """Health check endpoint for payslip service."""
        return {
            "service": "payslip_service", 
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_payslip_pdf(
        self,
        request: PayslipGenerationRequestDTO,
        hostname: str
    ) -> BytesIO:
        """
        Generate payslip PDF for a payout.
        
        Args:
            request: Payslip generation request
            hostname: Organization hostname
            
        Returns:
            PDF file as BytesIO buffer
        """
        try:
            logger.info(f"Generating PDF payslip for payout {request.payout_id}")
            
            # For now, return mock PDF data
            # In real implementation, this would call the service layer
            pdf_content = b"Mock PDF content for payslip"
            pdf_buffer = BytesIO(pdf_content)
            
            return pdf_buffer
            
        except Exception as e:
            logger.error(f"Error generating payslip PDF: {e}")
            raise
    
    async def email_payslip(
        self,
        request: PayslipEmailRequestDTO,
        hostname: str
    ) -> PayslipEmailResponseDTO:
        """
        Email payslip to employee.
        
        Args:
            request: Payslip email request
            hostname: Organization hostname
            
        Returns:
            Email operation response
        """
        try:
            logger.info(f"Emailing payslip for payout {request.payout_id}")
            
            # For now, return mock email response
            # In real implementation, this would call the service layer
            return PayslipEmailResponseDTO(
                payslip_id=f"PAYSLIP_{request.payout_id}",
                payout_id=request.payout_id,
                employee_id="EMP001",  # Would come from payout data
                recipient_email=request.recipient_email or "employee@company.com",
                email_status="sent",
                sent_at=datetime.now(),
                message="Payslip emailed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error emailing payslip: {e}")
            raise
    
    async def get_payslip_history(
        self,
        request: PayslipHistoryRequestDTO,
        hostname: str
    ) -> PayslipHistoryResponseDTO:
        """
        Get payslip history for an employee.
        
        Args:
            request: Payslip history request
            hostname: Organization hostname
            
        Returns:
            Employee payslip history
        """
        try:
            logger.info(f"Getting payslip history for employee {request.employee_id}")
            
            # For now, return mock history data
            # In real implementation, this would call the service layer
            payslip_responses = [
                PayslipResponseDTO(
                    payslip_id=f"PAYSLIP_{request.employee_id}_202401",
                    payout_id=f"PAYOUT_{request.employee_id}_202401",
                    employee_id=request.employee_id,
                    format="pdf",
                    status="generated",
                    generated_at=datetime(2024, 1, 31),
                    file_size=1024,
                    download_count=2
                )
            ]
            
            # Calculate statistics
            download_stats = {
                "total_downloads": sum(p.download_count for p in payslip_responses),
                "unique_months": len(set(p.generated_at.month for p in payslip_responses))
            }
            
            # Get last generated date
            last_generated = max(
                (p.generated_at for p in payslip_responses), 
                default=None
            )
            
            return PayslipHistoryResponseDTO(
                employee_id=request.employee_id,
                year=request.year,
                month=request.month,
                total_payslips=len(payslip_responses),
                payslips=payslip_responses,
                download_statistics=download_stats,
                last_generated=last_generated
            )
            
        except Exception as e:
            logger.error(f"Error getting payslip history: {e}")
            raise
    
    async def generate_bulk_payslips(
        self,
        request: BulkPayslipGenerationRequestDTO,
        hostname: str
    ) -> BulkPayslipOperationResponseDTO:
        """
        Generate payslips for multiple employees.
        
        Args:
            request: Bulk payslip generation request
            hostname: Organization hostname
            
        Returns:
            Bulk operation response
        """
        try:
            logger.info(f"Starting bulk payslip generation for {request.month:02d}/{request.year}")
            
            start_time = datetime.now()
            end_time = datetime.now()
            processing_duration = (end_time - start_time).total_seconds()
            
            # For now, return mock bulk operation response
            # In real implementation, this would call the service layer
            return BulkPayslipOperationResponseDTO(
                operation_id=f"BULK_GEN_{request.month}_{request.year}_{int(start_time.timestamp())}",
                operation_type="generate",
                status="completed",
                month=request.month,
                year=request.year,
                total_employees=10,  # Mock data
                processed_count=10,
                successful_count=10,
                failed_count=0,
                successful_operations=["EMP001", "EMP002"],  # Mock employee IDs
                failed_operations=[],
                started_at=start_time,
                completed_at=end_time,
                processing_duration=processing_duration
            )
            
        except Exception as e:
            logger.error(f"Error in bulk payslip generation: {e}")
            raise
    
    async def send_bulk_emails(
        self,
        request: BulkPayslipEmailRequestDTO,
        hostname: str
    ) -> BulkPayslipOperationResponseDTO:
        """
        Send payslips via email to multiple employees.
        
        Args:
            request: Bulk payslip email request
            hostname: Organization hostname
            
        Returns:
            Bulk operation response
        """
        try:
            logger.info(f"Starting bulk payslip email for {request.month:02d}/{request.year}")
            
            start_time = datetime.now()
            
            # For now, return mock bulk email response
            # In real implementation, this would call the service layer
            return BulkPayslipOperationResponseDTO(
                operation_id=f"BULK_EMAIL_{request.month}_{request.year}_{int(start_time.timestamp())}",
                operation_type="email",
                status="processing",  # Email operations are typically async
                month=request.month,
                year=request.year,
                total_employees=10,  # Mock data
                processed_count=0,  # Will be updated as emails are sent
                successful_count=0,
                failed_count=0,
                successful_operations=[],
                failed_operations=[],
                started_at=start_time,
                completed_at=None,  # Will be set when operation completes
                processing_duration=None
            )
            
        except Exception as e:
            logger.error(f"Error initiating bulk payslip email: {e}")
            raise
    
    async def get_bulk_operation_status(
        self,
        operation_id: str,
        hostname: str
    ) -> BulkPayslipOperationResponseDTO:
        """
        Get status of a bulk payslip operation.
        
        Args:
            operation_id: Bulk operation ID
            hostname: Organization hostname
            
        Returns:
            Bulk operation status
        """
        try:
            logger.info(f"Getting bulk operation status for {operation_id}")
            
            # For now, return mock status
            # In real implementation, this would query a background task status store
            return BulkPayslipOperationResponseDTO(
                operation_id=operation_id,
                operation_type="generate",  # Would be determined from stored data
                status="completed",
                month=1,  # Would be retrieved from stored data
                year=2024,   # Would be retrieved from stored data
                total_employees=10,
                processed_count=10,
                successful_count=10,
                failed_count=0,
                successful_operations=["EMP001", "EMP002"],
                failed_operations=[],
                started_at=datetime.now(),
                completed_at=datetime.now(),
                processing_duration=1.5
            )
            
        except Exception as e:
            logger.error(f"Error getting bulk operation status: {e}")
            raise
    
    async def get_monthly_summary(
        self,
        month: int,
        year: int,
        hostname: str
    ) -> PayslipSummaryResponseDTO:
        """
        Get payslip summary for a month.
        
        Args:
            month: Month
            year: Year
            hostname: Organization hostname
            
        Returns:
            Monthly payslip summary
        """
        try:
            logger.info(f"Getting payslip summary for {month:02d}/{year}")
            
            # For now, return mock summary
            # In real implementation, this would call a service to get actual summary data
            return PayslipSummaryResponseDTO(
                month=month,
                year=year,
                total_employees=10,
                payslips_generated=10,
                payslips_emailed=8,
                payslips_downloaded=5,
                pending_generation=0,
                failed_generation=0,
                generation_rate=100.0,
                email_delivery_rate=80.0,
                download_rate=50.0,
                last_generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting monthly payslip summary: {e}")
            raise
    
    async def create_schedule(
        self,
        request: PayslipScheduleRequestDTO,
        hostname: str
    ) -> PayslipScheduleResponseDTO:
        """
        Create a payslip generation schedule.
        
        Args:
            request: Payslip schedule request
            hostname: Organization hostname
            
        Returns:
            Created schedule response
        """
        try:
            logger.info(f"Creating payslip schedule for day {request.day_of_month}")
            
            # For now, return mock schedule response
            # In real implementation, this would call a service to create the schedule
            schedule_id = f"SCHEDULE_{datetime.now().timestamp()}"
            
            return PayslipScheduleResponseDTO(
                schedule_id=schedule_id,
                day_of_month=request.day_of_month,
                auto_email=request.auto_email,
                template_id=request.template_id,
                enabled=request.enabled,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error creating payslip schedule: {e}")
            raise
    
    async def get_templates(
        self,
        hostname: str
    ) -> List[PayslipTemplateResponseDTO]:
        """
        Get available payslip templates.
        
        Args:
            hostname: Organization hostname
            
        Returns:
            List of available templates
        """
        try:
            logger.info("Getting payslip templates")
            
            # For now, return mock templates
            # In real implementation, this would call a service to get templates
            return [
                PayslipTemplateResponseDTO(
                    template_id="default",
                    template_name="Default Template",
                    description="Standard payslip template",
                    is_default=True,
                    is_active=True,
                    created_at=datetime.now(),
                    usage_count=100
                )
            ]
            
        except Exception as e:
            logger.error(f"Error getting payslip templates: {e}")
            raise
    
    async def set_default_template(
        self,
        template_id: str,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Set default payslip template.
        
        Args:
            template_id: Template ID to set as default
            hostname: Organization hostname
            
        Returns:
            Operation result
        """
        try:
            logger.info(f"Setting default payslip template to {template_id}")
            
            # For now, return mock success response
            # In real implementation, this would call a service to update the default template
            return {
                "message": "Default template updated successfully",
                "template_id": template_id,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error setting default template: {e}")
            raise
    
    async def get_payslip_download_info(
        self,
        payout_id: str,
        hostname: str
    ) -> PayslipDownloadResponseDTO:
        """
        Get payslip download information.
        
        Args:
            payout_id: Payout ID
            hostname: Organization hostname
            
        Returns:
            Payslip download information
        """
        try:
            logger.info(f"Getting payslip download info for payout {payout_id}")
            
            # For now, return mock download info
            # In real implementation, this would call a service to get download info
            return PayslipDownloadResponseDTO(
                payslip_id=f"PAYSLIP_{payout_id}",
                payout_id=payout_id,
                employee_id="EMP001",  # Would be retrieved from service
                filename=f"payslip_{payout_id}.pdf",
                file_size=1024,  # Would be retrieved from service
                content_type="application/pdf"
            )
            
        except Exception as e:
            logger.error(f"Error getting payslip download info: {e}")
            raise
