"""
Project Attribute Domain Entity
Core business object for organization-specific configuration attributes
"""

from typing import Optional, Dict, Any, Union
from datetime import datetime
from app.domain.entities.base_entity import BaseEntity
from app.application.dto.project_attributes_dto import ValueType


class ProjectAttribute(BaseEntity):
    """
    Project Attribute domain entity.
    
    Represents organization-specific configuration attributes that can be used
    throughout the application for feature flags, settings, and configuration values.
    """
    
    def __init__(
        self,
        key: str,
        value: Union[str, bool, int, float],
        value_type: ValueType,
        description: Optional[str] = None,
        is_active: bool = True,
        default_value: Optional[Union[str, bool, int, float]] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        is_system: bool = False,
        created_by: Optional[str] = None,
        updated_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        id: Optional[str] = None
    ):
        """
        Initialize project attribute.
        
        Args:
            key: Unique identifier for the attribute
            value: Current value of the attribute
            value_type: Type of the value (boolean, string, number, etc.)
            description: Optional description of the attribute
            is_active: Whether the attribute is active
            default_value: Default value for the attribute
            validation_rules: Type-specific validation rules
            category: Category for grouping attributes
            is_system: Whether this is a system-managed attribute
            created_by: User who created the attribute
            updated_by: User who last updated the attribute
            created_at: Creation timestamp
            updated_at: Last update timestamp
            id: Unique identifier
        """
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        
        self._key = key
        self._value = value
        self._value_type = value_type
        self._description = description
        self._is_active = is_active
        self._default_value = default_value
        self._validation_rules = validation_rules or {}
        self._category = category
        self._is_system = is_system
        self._created_by = created_by
        self._updated_by = updated_by
        
        # Validate the value matches the type
        self._validate_value_type()
    
    @property
    def key(self) -> str:
        """Get attribute key."""
        return self._key
    
    @property
    def value(self) -> Union[str, bool, int, float]:
        """Get attribute value."""
        return self._value
    
    @property
    def value_type(self) -> ValueType:
        """Get value type."""
        return self._value_type
    
    @property
    def description(self) -> Optional[str]:
        """Get description."""
        return self._description
    
    @property
    def is_active(self) -> bool:
        """Get active status."""
        return self._is_active
    
    @property
    def default_value(self) -> Optional[Union[str, bool, int, float]]:
        """Get default value."""
        return self._default_value
    
    @property
    def validation_rules(self) -> Dict[str, Any]:
        """Get validation rules."""
        return self._validation_rules.copy()
    
    @property
    def category(self) -> Optional[str]:
        """Get category."""
        return self._category
    
    @property
    def is_system(self) -> bool:
        """Get system-managed status."""
        return self._is_system
    
    @property
    def created_by(self) -> Optional[str]:
        """Get creator."""
        return self._created_by
    
    @property
    def updated_by(self) -> Optional[str]:
        """Get last updater."""
        return self._updated_by
    
    def update_value(
        self, 
        value: Union[str, bool, int, float], 
        updated_by: str
    ) -> None:
        """
        Update attribute value.
        
        Args:
            value: New value
            updated_by: User updating the value
        """
        # Validate the new value matches the type
        if not self._is_valid_value_for_type(value, self._value_type):
            raise ValueError(f"Value {value} is not valid for type {self._value_type}")
        
        self._value = value
        self._updated_by = updated_by
        self._updated_at = datetime.utcnow()
    
    def update_description(self, description: str, updated_by: str) -> None:
        """
        Update description.
        
        Args:
            description: New description
            updated_by: User updating the description
        """
        self._description = description
        self._updated_by = updated_by
        self._updated_at = datetime.utcnow()
    
    def set_active_status(self, is_active: bool, updated_by: str) -> None:
        """
        Set active status.
        
        Args:
            is_active: New active status
            updated_by: User updating the status
        """
        self._is_active = is_active
        self._updated_by = updated_by
        self._updated_at = datetime.utcnow()
    
    def update_validation_rules(
        self, 
        validation_rules: Dict[str, Any], 
        updated_by: str
    ) -> None:
        """
        Update validation rules.
        
        Args:
            validation_rules: New validation rules
            updated_by: User updating the rules
        """
        self._validation_rules = validation_rules
        self._updated_by = updated_by
        self._updated_at = datetime.utcnow()
    
    def reset_to_default(self, updated_by: str) -> None:
        """
        Reset value to default.
        
        Args:
            updated_by: User resetting the value
        """
        if self._default_value is not None:
            self.update_value(self._default_value, updated_by)
    
    def is_boolean(self) -> bool:
        """Check if attribute is boolean type."""
        return self._value_type == ValueType.BOOLEAN
    
    def is_numeric(self) -> bool:
        """Check if attribute is numeric type."""
        return self._value_type == ValueType.NUMBER
    
    def is_text(self) -> bool:
        """Check if attribute is text type."""
        return self._value_type in [ValueType.STRING, ValueType.TEXT, ValueType.MULTILINE_TEXT]
    
    def is_dropdown(self) -> bool:
        """Check if attribute is dropdown type."""
        return self._value_type == ValueType.DROPDOWN
    
    def get_boolean_value(self) -> bool:
        """Get value as boolean."""
        if not self.is_boolean():
            raise ValueError(f"Attribute {self._key} is not boolean type")
        return bool(self._value)
    
    def get_numeric_value(self) -> Union[int, float]:
        """Get value as numeric."""
        if not self.is_numeric():
            raise ValueError(f"Attribute {self._key} is not numeric type")
        return float(self._value) if isinstance(self._value, str) else self._value
    
    def get_string_value(self) -> str:
        """Get value as string."""
        return str(self._value)
    
    def get_dropdown_options(self) -> list:
        """Get dropdown options from validation rules."""
        if not self.is_dropdown():
            raise ValueError(f"Attribute {self._key} is not dropdown type")
        return self._validation_rules.get('options', [])
    
    def validate_value(self, value: Union[str, bool, int, float]) -> bool:
        """
        Validate a value against the attribute's type and rules.
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            return self._is_valid_value_for_type(value, self._value_type)
        except ValueError:
            return False
    
    def _validate_value_type(self) -> None:
        """Validate that the current value matches the declared type."""
        if not self._is_valid_value_for_type(self._value, self._value_type):
            raise ValueError(f"Value {self._value} is not valid for type {self._value_type}")
    
    def _is_valid_value_for_type(
        self, 
        value: Union[str, bool, int, float], 
        value_type: ValueType
    ) -> bool:
        """
        Check if value is valid for the given type.
        
        Args:
            value: Value to check
            value_type: Expected type
            
        Returns:
            True if valid, False otherwise
        """
        if value_type == ValueType.BOOLEAN:
            return isinstance(value, bool)
        elif value_type == ValueType.NUMBER:
            return isinstance(value, (int, float)) or (
                isinstance(value, str) and self._is_numeric_string(value)
            )
        elif value_type == ValueType.EMAIL:
            return isinstance(value, str) and '@' in value
        elif value_type == ValueType.PHONE:
            return isinstance(value, str) and len(value) >= 10
        elif value_type == ValueType.URL:
            return isinstance(value, str) and value.startswith(('http://', 'https://'))
        elif value_type == ValueType.DATE:
            return isinstance(value, str) and self._is_valid_date(value)
        elif value_type == ValueType.DROPDOWN:
            if not isinstance(value, str):
                return False
            options = self._validation_rules.get('options', [])
            return value in options
        else:
            # STRING, TEXT, MULTILINE_TEXT, JSON
            return isinstance(value, str)
    
    def _is_numeric_string(self, value: str) -> bool:
        """Check if string represents a valid number."""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _is_valid_date(self, value: str) -> bool:
        """Check if string represents a valid date."""
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'key': self._key,
            'value': self._value,
            'value_type': self._value_type.value,
            'description': self._description,
            'is_active': self._is_active,
            'default_value': self._default_value,
            'validation_rules': self._validation_rules,
            'category': self._category,
            'is_system': self._is_system,
            'created_by': self._created_by,
            'updated_by': self._updated_by,
            'created_at': self._created_at.isoformat() if self._created_at else None,
            'updated_at': self._updated_at.isoformat() if self._updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectAttribute':
        """Create from dictionary."""
        
        return cls(
            id=data.get('id'),
            key=data['key'],
            value=data['value'],
            value_type=ValueType(data['value_type']),
            description=data.get('description'),
            is_active=data.get('is_active', True),
            default_value=data.get('default_value'),
            validation_rules=data.get('validation_rules', {}),
            category=data.get('category'),
            is_system=data.get('is_system', False),
            created_by=data.get('created_by'),
            updated_by=data.get('updated_by'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        ) 