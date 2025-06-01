"""
User Documents Value Object
Encapsulates user document information following DDD principles
"""

from dataclasses import dataclass
from typing import Optional, List
import os


@dataclass(frozen=True)
class UserDocuments:
    """
    Value object for user documents.
    
    Follows SOLID principles:
    - SRP: Only handles document-related operations
    - OCP: Can be extended with new document types
    - LSP: Can be substituted anywhere UserDocuments is expected
    - ISP: Focused interface for document operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    photo_path: Optional[str] = None
    pan_document_path: Optional[str] = None
    aadhar_document_path: Optional[str] = None
    
    def __post_init__(self):
        """Validate document paths after initialization"""
        self._validate_document_paths()
    
    def _validate_document_paths(self) -> None:
        """Validate document file paths"""
        paths = [self.photo_path, self.pan_document_path, self.aadhar_document_path]
        
        for path in paths:
            if path is not None and not isinstance(path, str):
                raise ValueError("Document paths must be strings")
            
            if path is not None and path.strip() == "":
                raise ValueError("Document paths cannot be empty strings")
    
    def has_photo(self) -> bool:
        """Check if user has uploaded a photo"""
        return bool(self.photo_path and self.photo_path.strip())
    
    def has_pan_document(self) -> bool:
        """Check if user has uploaded PAN document"""
        return bool(self.pan_document_path and self.pan_document_path.strip())
    
    def has_aadhar_document(self) -> bool:
        """Check if user has uploaded Aadhar document"""
        return bool(self.aadhar_document_path and self.aadhar_document_path.strip())
    
    def get_document_completion_percentage(self) -> float:
        """Get document completion percentage"""
        total_documents = 3  # photo, pan, aadhar
        completed_documents = 0
        
        if self.has_photo():
            completed_documents += 1
        if self.has_pan_document():
            completed_documents += 1
        if self.has_aadhar_document():
            completed_documents += 1
        
        return (completed_documents / total_documents) * 100
    
    def get_missing_documents(self) -> List[str]:
        """Get list of missing documents"""
        missing = []
        
        if not self.has_photo():
            missing.append("Photo")
        if not self.has_pan_document():
            missing.append("PAN Document")
        if not self.has_aadhar_document():
            missing.append("Aadhar Document")
        
        return missing
    
    def get_uploaded_documents(self) -> List[str]:
        """Get list of uploaded documents"""
        uploaded = []
        
        if self.has_photo():
            uploaded.append("Photo")
        if self.has_pan_document():
            uploaded.append("PAN Document")
        if self.has_aadhar_document():
            uploaded.append("Aadhar Document")
        
        return uploaded
    
    def is_complete(self) -> bool:
        """Check if all documents are uploaded"""
        return self.has_photo() and self.has_pan_document() and self.has_aadhar_document()
    
    def get_document_count(self) -> int:
        """Get count of uploaded documents"""
        count = 0
        if self.has_photo():
            count += 1
        if self.has_pan_document():
            count += 1
        if self.has_aadhar_document():
            count += 1
        return count
    
    def get_document_by_type(self, document_type: str) -> Optional[str]:
        """
        Get document path by type.
        
        Args:
            document_type: Type of document ('photo', 'pan', 'aadhar')
            
        Returns:
            Document path if exists, None otherwise
        """
        document_type = document_type.lower()
        
        if document_type == "photo":
            return self.photo_path
        elif document_type == "pan":
            return self.pan_document_path
        elif document_type == "aadhar":
            return self.aadhar_document_path
        else:
            raise ValueError(f"Unknown document type: {document_type}")
    
    def get_file_extension(self, document_type: str) -> Optional[str]:
        """
        Get file extension for a document type.
        
        Args:
            document_type: Type of document ('photo', 'pan', 'aadhar')
            
        Returns:
            File extension if document exists, None otherwise
        """
        path = self.get_document_by_type(document_type)
        if path:
            return os.path.splitext(path)[1].lower()
        return None
    
    def is_image_file(self, document_type: str) -> bool:
        """
        Check if document is an image file.
        
        Args:
            document_type: Type of document
            
        Returns:
            True if document is an image file
        """
        extension = self.get_file_extension(document_type)
        if extension:
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            return extension in image_extensions
        return False
    
    def is_pdf_file(self, document_type: str) -> bool:
        """
        Check if document is a PDF file.
        
        Args:
            document_type: Type of document
            
        Returns:
            True if document is a PDF file
        """
        extension = self.get_file_extension(document_type)
        return extension == '.pdf' if extension else False
    
    def get_document_recommendations(self) -> List[str]:
        """Get recommendations for document completion"""
        recommendations = []
        
        if not self.has_photo():
            recommendations.append("Upload a clear passport-size photograph")
        
        if not self.has_pan_document():
            recommendations.append("Upload a clear copy of your PAN card")
        
        if not self.has_aadhar_document():
            recommendations.append("Upload a clear copy of your Aadhar card")
        
        if self.is_complete():
            recommendations.append("All documents are uploaded. Thank you!")
        
        return recommendations
    
    def with_photo(self, photo_path: str) -> 'UserDocuments':
        """Create new instance with updated photo path"""
        return UserDocuments(
            photo_path=photo_path,
            pan_document_path=self.pan_document_path,
            aadhar_document_path=self.aadhar_document_path
        )
    
    def with_pan_document(self, pan_document_path: str) -> 'UserDocuments':
        """Create new instance with updated PAN document path"""
        return UserDocuments(
            photo_path=self.photo_path,
            pan_document_path=pan_document_path,
            aadhar_document_path=self.aadhar_document_path
        )
    
    def with_aadhar_document(self, aadhar_document_path: str) -> 'UserDocuments':
        """Create new instance with updated Aadhar document path"""
        return UserDocuments(
            photo_path=self.photo_path,
            pan_document_path=self.pan_document_path,
            aadhar_document_path=aadhar_document_path
        )
    
    def without_photo(self) -> 'UserDocuments':
        """Create new instance without photo"""
        return UserDocuments(
            photo_path=None,
            pan_document_path=self.pan_document_path,
            aadhar_document_path=self.aadhar_document_path
        )
    
    def without_pan_document(self) -> 'UserDocuments':
        """Create new instance without PAN document"""
        return UserDocuments(
            photo_path=self.photo_path,
            pan_document_path=None,
            aadhar_document_path=self.aadhar_document_path
        )
    
    def without_aadhar_document(self) -> 'UserDocuments':
        """Create new instance without Aadhar document"""
        return UserDocuments(
            photo_path=self.photo_path,
            pan_document_path=self.pan_document_path,
            aadhar_document_path=None
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "photo_path": self.photo_path,
            "pan_document_path": self.pan_document_path,
            "aadhar_document_path": self.aadhar_document_path,
            "has_photo": self.has_photo(),
            "has_pan_document": self.has_pan_document(),
            "has_aadhar_document": self.has_aadhar_document(),
            "completion_percentage": self.get_document_completion_percentage(),
            "missing_documents": self.get_missing_documents(),
            "uploaded_documents": self.get_uploaded_documents(),
            "is_complete": self.is_complete(),
            "document_count": self.get_document_count(),
            "recommendations": self.get_document_recommendations()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserDocuments':
        """Create from dictionary"""
        return cls(
            photo_path=data.get("photo_path"),
            pan_document_path=data.get("pan_document_path"),
            aadhar_document_path=data.get("aadhar_document_path")
        )
    
    @classmethod
    def empty(cls) -> 'UserDocuments':
        """Create empty documents instance"""
        return cls()
    
    def __str__(self) -> str:
        """String representation"""
        return f"UserDocuments(completion={self.get_document_completion_percentage():.1f}%, count={self.get_document_count()}/3)"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"UserDocuments(photo={bool(self.photo_path)}, pan={bool(self.pan_document_path)}, aadhar={bool(self.aadhar_document_path)})" 