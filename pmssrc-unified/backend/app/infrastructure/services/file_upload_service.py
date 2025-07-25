"""
File Upload Service Implementation
SOLID-compliant service for file upload operations
"""

import logging
import os
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
from abc import ABC, abstractmethod
from fastapi import UploadFile
import aiofiles

logger = logging.getLogger(__name__)


class FileUploadService(ABC):
    """
    Abstract file upload service interface.
    
    Follows SOLID principles:
    - SRP: Only handles file upload operations
    - OCP: Can be extended with new storage backends
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for file operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def upload_document(
        self, 
        file: UploadFile, 
        document_type: str,
        employee_id: Optional[str] = None
    ) -> str:
        """Upload a document and return the file path."""
        pass
    
    @abstractmethod
    async def delete_document(self, file_path: str) -> bool:
        """Delete a document by file path."""
        pass
    
    @abstractmethod
    async def get_document_url(self, file_path: str) -> str:
        """Get public URL for a document."""
        pass
    
    @abstractmethod
    def validate_file(self, file: UploadFile, document_type: str) -> Dict[str, Any]:
        """Validate file before upload."""
        pass


class LocalFileUploadService(FileUploadService):
    """
    Local file system implementation of file upload service.
    
    Stores files on the local file system following SOLID principles.
    """
    
    def __init__(self, base_upload_path: str = "uploads"):
        """
        Initialize local file upload service.
        
        Args:
            base_upload_path: Base directory for file uploads
        """
        self.base_upload_path = Path(base_upload_path)
        self.base_upload_path.mkdir(parents=True, exist_ok=True)
        
        # Document type configurations
        self.document_configs = {
            "photo": {
                "allowed_extensions": [".jpg", ".jpeg", ".png", ".gif"],
                "max_size_mb": 5,
                "subfolder": "photos"
            },
            "pan": {
                "allowed_extensions": [".jpg", ".jpeg", ".png", ".pdf"],
                "max_size_mb": 2,
                "subfolder": "pan"
            },
            "aadhar": {
                "allowed_extensions": [".jpg", ".jpeg", ".png", ".pdf"],
                "max_size_mb": 2,
                "subfolder": "aadhar"
            },
            "reimbursement": {
                "allowed_extensions": [".jpg", ".jpeg", ".png", ".pdf"],
                "max_size_mb": 10,
                "subfolder": "reimbursements"
            },
            "receipt": {
                "allowed_extensions": [".jpg", ".jpeg", ".png", ".pdf"],
                "max_size_mb": 10,
                "subfolder": "receipts"
            }
        }
    
    async def upload_document(
        self, 
        file: UploadFile, 
        document_type: str,
        employee_id: Optional[str] = None
    ) -> str:
        """
        Upload a document to local file system.
        
        Args:
            file: File to upload
            document_type: Type of document (photo, pan, aadhar, etc.)
            employee_id: Optional user ID for organizing files
            
        Returns:
            Relative file path of uploaded file
            
        Raises:
            ValueError: If file validation fails
            IOError: If file upload fails
        """
        try:
            # Validate file
            validation_result = self.validate_file(file, document_type)
            if not validation_result["is_valid"]:
                raise ValueError(f"File validation failed: {validation_result['errors']}")
            
            # Get document configuration
            config = self.document_configs.get(document_type)
            if not config:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Create directory structure
            subfolder = config["subfolder"]
            upload_dir = self.base_upload_path / subfolder
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Add employee_id to path if provided
            if employee_id:
                user_dir = upload_dir / employee_id
                user_dir.mkdir(parents=True, exist_ok=True)
                file_path = user_dir / unique_filename
                relative_path = f"{subfolder}/{employee_id}/{unique_filename}"
            else:
                file_path = upload_dir / unique_filename
                relative_path = f"{subfolder}/{unique_filename}"
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"File uploaded successfully: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            raise
    
    async def delete_document(self, file_path: str) -> bool:
        """
        Delete a document from local file system.
        
        Args:
            file_path: Relative path of file to delete
            
        Returns:
            True if file deleted successfully, False otherwise
        """
        try:
            full_path = self.base_upload_path / file_path
            
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    async def get_document_url(self, file_path: str) -> str:
        """
        Get public URL for a document.
        
        Args:
            file_path: Relative path of file
            
        Returns:
            Public URL for the file
        """
        # For local files, return a relative URL that can be served by the web server
        return f"/uploads/{file_path}"
    
    def validate_file(self, file: UploadFile, document_type: str) -> Dict[str, Any]:
        """
        Validate file before upload.
        
        Args:
            file: File to validate
            document_type: Type of document
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Get document configuration
        config = self.document_configs.get(document_type)
        if not config:
            return {
                "is_valid": False,
                "errors": [f"Unsupported document type: {document_type}"],
                "warnings": []
            }
        
        # Check if file is provided
        if not file or not file.filename:
            errors.append("No file provided")
            return {
                "is_valid": False,
                "errors": errors,
                "warnings": warnings
            }
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        allowed_extensions = config["allowed_extensions"]
        
        if file_extension not in allowed_extensions:
            errors.append(
                f"Invalid file extension '{file_extension}'. "
                f"Allowed extensions: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        if hasattr(file, 'size') and file.size:
            max_size_bytes = config["max_size_mb"] * 1024 * 1024
            if file.size > max_size_bytes:
                errors.append(
                    f"File size ({file.size / 1024 / 1024:.2f} MB) exceeds "
                    f"maximum allowed size ({config['max_size_mb']} MB)"
                )
        
        # Check filename length
        if len(file.filename) > 255:
            errors.append("Filename is too long (maximum 255 characters)")
        
        # Check for potentially dangerous filenames
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(char in file.filename for char in dangerous_chars):
            errors.append("Filename contains invalid characters")
        
        # Additional validation based on document type
        if document_type == "photo":
            if file_extension not in [".jpg", ".jpeg", ".png", ".gif"]:
                warnings.append("Photo should be in JPG, PNG, or GIF format for best compatibility")
        
        elif document_type in ["pan", "aadhar"]:
            if file_extension not in [".jpg", ".jpeg", ".png", ".pdf"]:
                warnings.append("Document should be in JPG, PNG, or PDF format")
        
        is_valid = len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "file_info": {
                "filename": file.filename,
                "extension": file_extension,
                "size_mb": file.size / 1024 / 1024 if hasattr(file, 'size') and file.size else None,
                "content_type": file.content_type
            }
        }
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an uploaded file.
        
        Args:
            file_path: Relative path of file
            
        Returns:
            Dictionary with file information or None if file not found
        """
        try:
            full_path = self.base_upload_path / file_path
            
            if not full_path.exists():
                return None
            
            stat = full_path.stat()
            
            return {
                "path": file_path,
                "filename": full_path.name,
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / 1024 / 1024,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "extension": full_path.suffix.lower()
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None


class S3FileUploadService(FileUploadService):
    """
    AWS S3 implementation of file upload service.
    
    Stores files in AWS S3 following SOLID principles.
    """
    
    def __init__(self, bucket_name: str, aws_access_key: str, aws_secret_key: str, region: str = "us-east-1"):
        """
        Initialize S3 file upload service.
        
        Args:
            bucket_name: S3 bucket name
            aws_access_key: AWS access key
            aws_secret_key: AWS secret key
            region: AWS region
        """
        self.bucket_name = bucket_name
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.region = region
        
        # Initialize S3 client (would use boto3 in real implementation)
        # self.s3_client = boto3.client('s3', ...)
    
    async def upload_document(
        self, 
        file: UploadFile, 
        document_type: str,
        employee_id: Optional[str] = None
    ) -> str:
        """Upload document to S3."""
        # Implementation would use boto3 to upload to S3
        # For now, return a mock path
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        s3_key = f"{document_type}/{employee_id}/{unique_filename}" if employee_id else f"{document_type}/{unique_filename}"
        
        # Mock S3 upload
        logger.info(f"Mock S3 upload: {s3_key}")
        return s3_key
    
    async def delete_document(self, file_path: str) -> bool:
        """Delete document from S3."""
        # Implementation would use boto3 to delete from S3
        logger.info(f"Mock S3 delete: {file_path}")
        return True
    
    async def get_document_url(self, file_path: str) -> str:
        """Get S3 URL for document."""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_path}"
    
    def validate_file(self, file: UploadFile, document_type: str) -> Dict[str, Any]:
        """Validate file (same logic as local service)."""
        # Reuse validation logic from LocalFileUploadService
        local_service = LocalFileUploadService()
        return local_service.validate_file(file, document_type)


class FileUploadServiceFactory:
    """
    Factory for creating file upload service instances.
    
    Follows the Factory pattern to create appropriate file upload services
    based on configuration.
    """
    
    @staticmethod
    def create_service(storage_type: str = "local", **kwargs) -> FileUploadService:
        """
        Create file upload service based on storage type.
        
        Args:
            storage_type: Type of storage ("local" or "s3")
            **kwargs: Additional configuration parameters
            
        Returns:
            File upload service instance
            
        Raises:
            ValueError: If storage type is not supported
        """
        if storage_type == "local":
            base_path = kwargs.get("base_upload_path", "uploads")
            return LocalFileUploadService(base_path)
        
        elif storage_type == "s3":
            required_params = ["bucket_name", "aws_access_key", "aws_secret_key"]
            for param in required_params:
                if param not in kwargs:
                    raise ValueError(f"Missing required parameter for S3: {param}")
            
            return S3FileUploadService(
                bucket_name=kwargs["bucket_name"],
                aws_access_key=kwargs["aws_access_key"],
                aws_secret_key=kwargs["aws_secret_key"],
                region=kwargs.get("region", "us-east-1")
            )
        
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")


# Document type enum for type safety
class DocumentType:
    """Document type constants."""
    PHOTO = "photo"
    PAN = "pan"
    AADHAR = "aadhar"
    REIMBURSEMENT = "reimbursement"
    RECEIPT = "receipt" 