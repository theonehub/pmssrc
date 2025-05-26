import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import calendar
from io import BytesIO
import json
from fastapi import HTTPException
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

from database.payout_database import PayoutDatabase
from services.payout_service import get_employee_payouts_service, generate_payslip_data_service
from services.user_service import get_user_by_emp_id, get_all_users
from services.organisation_service import get_organisation_by_hostname
from models.payout import PayoutInDB, PayoutStatus, PayslipData

logger = logging.getLogger(__name__)

class PayslipService:
    """Comprehensive payslip service for PDF generation, email distribution, and automation"""
    
    def __init__(self, hostname: str):
        self.hostname = hostname
        self.payout_db = PayoutDatabase(hostname)
        
    def generate_payslip_pdf(self, payout_id: str) -> BytesIO:
        """
        Generate a professional PDF payslip for a given payout
        
        Args:
            payout_id: ID of the payout record
            
        Returns:
            BytesIO: PDF file buffer
        """
        try:
            # Get payslip data
            payslip_data = generate_payslip_data_service(payout_id, self.hostname)
            
            # Get organization details
            try:
                organization = get_organisation_by_hostname(self.hostname)
                if organization:
                    payslip_data.company_name = organization.name
                    payslip_data.company_address = f"{organization.address}, {organization.city}, {organization.state} - {organization.pin_code}"
            except Exception as e:
                logger.warning(f"Could not fetch organization details: {str(e)}")
            
            # Create PDF buffer
            buffer = BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # Build PDF content
            story = self._build_payslip_content(payslip_data)
            
            # Generate PDF
            doc.build(story)
            
            # Reset buffer position
            buffer.seek(0)
            
            logger.info(f"Generated PDF payslip for payout {payout_id}")
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF payslip: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating PDF payslip: {str(e)}")
    
    def _build_payslip_content(self, payslip_data: PayslipData) -> List:
        """Build the content structure for the PDF payslip"""
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Company Header
        story.append(Paragraph(payslip_data.company_name, title_style))
        if payslip_data.company_address:
            story.append(Paragraph(payslip_data.company_address, normal_style))
        story.append(Spacer(1, 12))
        
        # Payslip Title
        story.append(Paragraph("SALARY SLIP", header_style))
        story.append(Spacer(1, 12))
        
        # Employee and Pay Period Information
        info_data = [
            ['Employee Information', '', 'Pay Period Information', ''],
            ['Name:', payslip_data.employee_name, 'Pay Period:', payslip_data.pay_period],
            ['Employee Code:', payslip_data.employee_code or 'N/A', 'Pay Date:', payslip_data.payout_date],
            ['Department:', payslip_data.department or 'N/A', 'Days in Month:', str(payslip_data.days_in_month)],
            ['Designation:', payslip_data.designation or 'N/A', 'Days Worked:', str(payslip_data.days_worked)],
            ['PAN:', payslip_data.pan_number or 'N/A', 'LWP Days:', str(payslip_data.lwp_days)],
            ['UAN:', payslip_data.uan_number or 'N/A', 'Effective Working Days:', str(payslip_data.effective_working_days)],
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Earnings and Deductions Table
        earnings_deductions_data = [
            ['EARNINGS', 'AMOUNT (₹)', 'DEDUCTIONS', 'AMOUNT (₹)']
        ]
        
        # Prepare earnings and deductions lists
        earnings_list = list(payslip_data.earnings.items())
        deductions_list = list(payslip_data.deductions.items())
        
        # Make both lists the same length
        max_rows = max(len(earnings_list), len(deductions_list))
        
        for i in range(max_rows):
            earning_name = earnings_list[i][0] if i < len(earnings_list) else ''
            earning_amount = f"{earnings_list[i][1]:,.2f}" if i < len(earnings_list) else ''
            deduction_name = deductions_list[i][0] if i < len(deductions_list) else ''
            deduction_amount = f"{deductions_list[i][1]:,.2f}" if i < len(deductions_list) else ''
            
            earnings_deductions_data.append([
                earning_name, earning_amount, deduction_name, deduction_amount
            ])
        
        # Add totals row
        earnings_deductions_data.append([
            'TOTAL EARNINGS', f"{payslip_data.total_earnings:,.2f}",
            'TOTAL DEDUCTIONS', f"{payslip_data.total_deductions:,.2f}"
        ])
        
        ed_table = Table(earnings_deductions_data, colWidths=[2.5*inch, 1*inch, 2.5*inch, 1*inch])
        ed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(ed_table)
        story.append(Spacer(1, 20))
        
        # Net Pay
        net_pay_data = [
            ['NET PAY', f"₹ {payslip_data.net_pay:,.2f}"]
        ]
        
        net_pay_table = Table(net_pay_data, colWidths=[5*inch, 2*inch])
        net_pay_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(net_pay_table)
        story.append(Spacer(1, 20))
        
        # Year to Date Information
        ytd_data = [
            ['Year to Date Information', ''],
            ['YTD Gross Earnings:', f"₹ {payslip_data.ytd_gross:,.2f}"],
            ['YTD Tax Deducted:', f"₹ {payslip_data.ytd_tax_deducted:,.2f}"],
            ['Tax Regime:', payslip_data.tax_regime.upper()],
        ]
        
        ytd_table = Table(ytd_data, colWidths=[4*inch, 3*inch])
        ytd_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(ytd_table)
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = "This is a computer-generated payslip and does not require a signature."
        story.append(Paragraph(footer_text, normal_style))
        
        return story
    
    def generate_monthly_payslips_bulk(self, month: int, year: int, status_filter: Optional[PayoutStatus] = None) -> Dict[str, Any]:
        """
        Generate payslips for all employees for a given month
        
        Args:
            month: Month (1-12)
            year: Year
            status_filter: Optional status filter for payouts
            
        Returns:
            Dictionary with generation results
        """
        try:
            logger.info(f"Starting bulk payslip generation for {month:02d}/{year}")
            
            # Get all payouts for the month
            payouts = self.payout_db.get_monthly_payouts(month, year, status_filter)
            
            # Filter only processed/approved/paid payouts
            eligible_payouts = [p for p in payouts if p.status in [PayoutStatus.PROCESSED, PayoutStatus.APPROVED, PayoutStatus.PAID]]
            
            successful_generations = []
            failed_generations = []
            
            for payout in eligible_payouts:
                try:
                    # Generate PDF
                    pdf_buffer = self.generate_payslip_pdf(payout.id)
                    
                    # Save PDF to file system (optional)
                    filename = f"payslip_{payout.employee_id}_{month:02d}_{year}.pdf"
                    filepath = self._save_payslip_pdf(pdf_buffer, filename)
                    
                    successful_generations.append({
                        "employee_id": payout.employee_id,
                        "payout_id": payout.id,
                        "filename": filename,
                        "filepath": filepath
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to generate payslip for {payout.employee_id}: {str(e)}")
                    failed_generations.append({
                        "employee_id": payout.employee_id,
                        "payout_id": payout.id,
                        "error": str(e)
                    })
            
            result = {
                "month": month,
                "year": year,
                "total_payouts": len(eligible_payouts),
                "successful_generations": len(successful_generations),
                "failed_generations": len(failed_generations),
                "generated_payslips": successful_generations,
                "errors": failed_generations
            }
            
            logger.info(f"Bulk payslip generation completed: {len(successful_generations)} successful, {len(failed_generations)} failed")
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk payslip generation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in bulk payslip generation: {str(e)}")
    
    def _save_payslip_pdf(self, pdf_buffer: BytesIO, filename: str) -> str:
        """Save PDF buffer to file system"""
        try:
            # Create payslips directory if it doesn't exist
            payslips_dir = f"payslips/{self.hostname}"
            os.makedirs(payslips_dir, exist_ok=True)
            
            # Save file
            filepath = os.path.join(payslips_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving payslip PDF: {str(e)}")
            raise
    
    def email_payslip(self, payout_id: str, recipient_email: Optional[str] = None) -> Dict[str, str]:
        """
        Email payslip to employee
        
        Args:
            payout_id: ID of the payout record
            recipient_email: Optional email override
            
        Returns:
            Dictionary with email status
        """
        try:
            # Get payout and employee details
            payout = self.payout_db.get_payout_by_id(payout_id)
            if not payout:
                raise HTTPException(status_code=404, detail="Payout not found")
            
            employee = get_user_by_emp_id(payout.employee_id, self.hostname)
            if not employee:
                raise HTTPException(status_code=404, detail="Employee not found")
            
            # Use provided email or employee's email
            email = recipient_email or employee.get('email')
            if not email:
                raise HTTPException(status_code=400, detail="No email address available")
            
            # Generate PDF
            pdf_buffer = self.generate_payslip_pdf(payout_id)
            
            # Get organization details for email
            organization = get_organisation_by_hostname(self.hostname)
            company_name = organization.name if organization else "Company"
            
            # Send email
            self._send_payslip_email(
                recipient_email=email,
                employee_name=employee.get('name', 'Employee'),
                company_name=company_name,
                pay_period=f"{payout.pay_period_start.strftime('%B %Y')}",
                pdf_buffer=pdf_buffer,
                filename=f"payslip_{payout.employee_id}_{payout.pay_period_start.strftime('%m_%Y')}.pdf"
            )
            
            logger.info(f"Payslip emailed successfully to {email} for payout {payout_id}")
            return {"message": "Payslip emailed successfully", "email": email}
            
        except Exception as e:
            logger.error(f"Error emailing payslip: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error emailing payslip: {str(e)}")
    
    def _send_payslip_email(self, recipient_email: str, employee_name: str, company_name: str, 
                           pay_period: str, pdf_buffer: BytesIO, filename: str):
        """Send payslip email with PDF attachment"""
        
        # Email configuration (should be moved to environment variables)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        if not smtp_username or not smtp_password:
            raise HTTPException(status_code=500, detail="Email configuration not found")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = f"Payslip for {pay_period} - {company_name}"
        
        # Email body
        body = f"""
        Dear {employee_name},

        Please find attached your payslip for {pay_period}.

        If you have any questions regarding your payslip, please contact the HR department.

        Best regards,
        {company_name} HR Team
        
        ---
        This is an automated email. Please do not reply to this email.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        pdf_attachment = MIMEBase('application', 'octet-stream')
        pdf_attachment.set_payload(pdf_buffer.getvalue())
        encoders.encode_base64(pdf_attachment)
        pdf_attachment.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        msg.attach(pdf_attachment)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, recipient_email, text)
        server.quit()
    
    def bulk_email_payslips(self, month: int, year: int) -> Dict[str, Any]:
        """
        Email payslips to all employees for a given month
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            Dictionary with email results
        """
        try:
            logger.info(f"Starting bulk payslip email for {month:02d}/{year}")
            
            # Get all processed payouts for the month
            payouts = self.payout_db.get_monthly_payouts(month, year, PayoutStatus.PROCESSED)
            
            successful_emails = []
            failed_emails = []
            
            for payout in payouts:
                try:
                    result = self.email_payslip(payout.id)
                    successful_emails.append({
                        "employee_id": payout.employee_id,
                        "payout_id": payout.id,
                        "email": result["email"]
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to email payslip for {payout.employee_id}: {str(e)}")
                    failed_emails.append({
                        "employee_id": payout.employee_id,
                        "payout_id": payout.id,
                        "error": str(e)
                    })
            
            result = {
                "month": month,
                "year": year,
                "total_payouts": len(payouts),
                "successful_emails": len(successful_emails),
                "failed_emails": len(failed_emails),
                "emailed_payslips": successful_emails,
                "errors": failed_emails
            }
            
            logger.info(f"Bulk payslip email completed: {len(successful_emails)} successful, {len(failed_emails)} failed")
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk payslip email: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in bulk payslip email: {str(e)}")
    
    def get_payslip_history(self, employee_id: str, year: int) -> List[Dict[str, Any]]:
        """
        Get payslip history for an employee
        
        Args:
            employee_id: Employee ID
            year: Year
            
        Returns:
            List of payslip records
        """
        try:
            payouts = get_employee_payouts_service(employee_id, self.hostname, year=year)
            
            payslip_history = []
            for payout in payouts:
                if payout.status in [PayoutStatus.PROCESSED, PayoutStatus.APPROVED, PayoutStatus.PAID]:
                    payslip_history.append({
                        "payout_id": payout.id,
                        "pay_period": f"{payout.pay_period_start.strftime('%B %Y')}",
                        "pay_period_start": payout.pay_period_start,
                        "pay_period_end": payout.pay_period_end,
                        "payout_date": payout.payout_date,
                        "gross_salary": payout.gross_salary,
                        "net_salary": payout.net_salary,
                        "status": payout.status,
                        "generated_date": payout.created_at if hasattr(payout, 'created_at') else None
                    })
            
            return sorted(payslip_history, key=lambda x: x['pay_period_start'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting payslip history: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting payslip history: {str(e)}")

# Service functions for backward compatibility
def generate_payslip_pdf_service(payout_id: str, hostname: str) -> BytesIO:
    """Generate PDF payslip for a payout"""
    service = PayslipService(hostname)
    return service.generate_payslip_pdf(payout_id)

def generate_monthly_payslips_bulk_service(month: int, year: int, hostname: str, status_filter: Optional[PayoutStatus] = None) -> Dict[str, Any]:
    """Generate payslips for all employees for a month"""
    service = PayslipService(hostname)
    return service.generate_monthly_payslips_bulk(month, year, status_filter)

def email_payslip_service(payout_id: str, hostname: str, recipient_email: Optional[str] = None) -> Dict[str, str]:
    """Email payslip to employee"""
    service = PayslipService(hostname)
    return service.email_payslip(payout_id, recipient_email)

def bulk_email_payslips_service(month: int, year: int, hostname: str) -> Dict[str, Any]:
    """Email payslips to all employees for a month"""
    service = PayslipService(hostname)
    return service.bulk_email_payslips(month, year)

def get_payslip_history_service(employee_id: str, year: int, hostname: str) -> List[Dict[str, Any]]:
    """Get payslip history for an employee"""
    service = PayslipService(hostname)
    return service.get_payslip_history(employee_id, year) 