"""
Table Logger Utility
Provides flexible table formatting for logs throughout the project
"""

from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from app.utils.logger import get_simple_logger

s_logger = get_simple_logger()


class TableStyle(Enum):
    """Available table styles."""
    SIMPLE = "simple"           # Basic ASCII borders
    UNICODE = "unicode"         # Unicode box-drawing characters
    MINIMAL = "minimal"         # No borders, just aligned columns
    COMPACT = "compact"         # Minimal spacing


@dataclass
class TableColumn:
    """Represents a table column configuration."""
    name: str
    width: int
    align: str = "left"  # left, right, center
    formatter: Optional[Callable] = None
    
    def format_value(self, value: Any) -> str:
        """Format a value using the column's formatter."""
        if self.formatter:
            return str(self.formatter(value))
        return str(value)


class TableLogger:
    """Utility class for creating formatted tables in logs."""
    
    def __init__(self, style: TableStyle = TableStyle.UNICODE):
        self.style = style
        self.logger = s_logger
    
    def _get_border_chars(self) -> Dict[str, str]:
        """Get border characters based on style."""
        if self.style == TableStyle.UNICODE:
            return {
                'top_left': '╔', 'top_right': '╗', 'top_middle': '╦',
                'bottom_left': '╚', 'bottom_right': '╝', 'bottom_middle': '╩',
                'left_middle': '╠', 'right_middle': '╣', 'middle_middle': '╬',
                'horizontal': '═', 'vertical': '║', 'separator': '│'
            }
        elif self.style == TableStyle.SIMPLE:
            return {
                'top_left': '+', 'top_right': '+', 'top_middle': '+',
                'bottom_left': '+', 'bottom_right': '+', 'bottom_middle': '+',
                'left_middle': '+', 'right_middle': '+', 'middle_middle': '+',
                'horizontal': '-', 'vertical': '|', 'separator': '|'
            }
        else:  # MINIMAL or COMPACT
            return {
                'top_left': '', 'top_right': '', 'top_middle': '',
                'bottom_left': '', 'bottom_right': '', 'bottom_middle': '',
                'left_middle': '', 'right_middle': '', 'middle_middle': '',
                'horizontal': '', 'vertical': '', 'separator': '  '
            }
    
    def _create_header_row(self, columns: List[TableColumn], border_chars: Dict[str, str]) -> str:
        """Create the header row with borders."""
        if self.style in [TableStyle.MINIMAL, TableStyle.COMPACT]:
            return self._create_minimal_header(columns)
        
        # Create header content
        header_cells = []
        for col in columns:
            if col.align == "center":
                cell = col.name.center(col.width)
            elif col.align == "right":
                cell = col.name.rjust(col.width)
            else:
                cell = col.name.ljust(col.width)
            header_cells.append(cell)
        
        header_content = f" {border_chars['separator']} ".join(header_cells)
        return f"{border_chars['vertical']} {header_content} {border_chars['vertical']}"
    
    def _create_minimal_header(self, columns: List[TableColumn]) -> str:
        """Create minimal header without borders."""
        header_cells = []
        for col in columns:
            if col.align == "center":
                cell = col.name.center(col.width)
            elif col.align == "right":
                cell = col.name.rjust(col.width)
            else:
                cell = col.name.ljust(col.width)
            header_cells.append(cell)
        
        return "  ".join(header_cells)
    
    def _create_separator_row(self, columns: List[TableColumn], border_chars: Dict[str, str]) -> str:
        """Create separator row between header and data."""
        if self.style in [TableStyle.MINIMAL, TableStyle.COMPACT]:
            return ""
        
        separator_parts = []
        for col in columns:
            separator_parts.append(border_chars['horizontal'] * col.width)
        
        separator_content = f" {border_chars['separator']} ".join(separator_parts)
        return f"{border_chars['left_middle']} {separator_content} {border_chars['right_middle']}"
    
    def _create_data_row(self, row_data: List[Any], columns: List[TableColumn], border_chars: Dict[str, str]) -> str:
        """Create a data row with proper formatting."""
        if self.style in [TableStyle.MINIMAL, TableStyle.COMPACT]:
            return self._create_minimal_data_row(row_data, columns)
        
        # Format each cell
        formatted_cells = []
        for i, (col, value) in enumerate(zip(columns, row_data)):
            formatted_value = col.format_value(value)
            
            if col.align == "center":
                cell = formatted_value.center(col.width)
            elif col.align == "right":
                cell = formatted_value.rjust(col.width)
            else:
                cell = formatted_value.ljust(col.width)
            
            formatted_cells.append(cell)
        
        row_content = f" {border_chars['separator']} ".join(formatted_cells)
        return f"{border_chars['vertical']} {row_content} {border_chars['vertical']}"
    
    def _create_minimal_data_row(self, row_data: List[Any], columns: List[TableColumn]) -> str:
        """Create minimal data row without borders."""
        formatted_cells = []
        for col, value in zip(columns, row_data):
            formatted_value = col.format_value(value)
            
            if col.align == "center":
                cell = formatted_value.center(col.width)
            elif col.align == "right":
                cell = formatted_value.rjust(col.width)
            else:
                cell = formatted_value.ljust(col.width)
            
            formatted_cells.append(cell)
        
        return "  ".join(formatted_cells)
    
    def _create_top_border(self, columns: List[TableColumn], border_chars: Dict[str, str]) -> str:
        """Create top border of the table."""
        if self.style in [TableStyle.MINIMAL, TableStyle.COMPACT]:
            return ""
        
        border_parts = []
        for col in columns:
            border_parts.append(border_chars['horizontal'] * col.width)
        
        border_content = f" {border_chars['separator']} ".join(border_parts)
        return f"{border_chars['top_left']} {border_content} {border_chars['top_right']}"
    
    def _create_bottom_border(self, columns: List[TableColumn], border_chars: Dict[str, str]) -> str:
        """Create bottom border of the table."""
        if self.style in [TableStyle.MINIMAL, TableStyle.COMPACT]:
            return ""
        
        border_parts = []
        for col in columns:
            border_parts.append(border_chars['horizontal'] * col.width)
        
        border_content = f" {border_chars['separator']} ".join(border_parts)
        return f"{border_chars['bottom_left']} {border_content} {border_chars['bottom_right']}"
    
    def log_table(self, 
                  title: str,
                  columns: List[TableColumn],
                  data: List[List[Any]],
                  show_status: bool = False,
                  status_checker: Optional[Callable[[List[Any]], bool]] = None) -> None:
        """
        Log a formatted table.
        
        Args:
            title: Table title
            columns: Column definitions
            data: Table data as list of rows
            show_status: Whether to show status indicators
            status_checker: Function to check if a row has positive status
        """
        border_chars = self._get_border_chars()
        
        # Log title
        if title:
            if self.style == TableStyle.UNICODE:
                title_line = f"║ {title.center(80)} ║"
                self.logger.info(f"╔{'═' * 84}╗")
                self.logger.info(title_line)
                self.logger.info(f"╠{'═' * 84}╣")
            else:
                self.logger.info(f"=== {title} ===")
        
        # Create top border
        top_border = self._create_top_border(columns, border_chars)
        if top_border:
            self.logger.info(top_border)
        
        # Create header
        header = self._create_header_row(columns, border_chars)
        self.logger.info(header)
        
        # Create separator
        separator = self._create_separator_row(columns, border_chars)
        if separator:
            self.logger.info(separator)
        
        # Create data rows
        for row_data in data:
            if show_status and status_checker:
                # Add status indicator to the row
                status = status_checker(row_data)
                status_symbol = "✓" if status else "✗"
                row_with_status = row_data + [status_symbol]
                
                # Create temporary column for status
                status_col = TableColumn("Status", 8, "center")
                temp_columns = columns + [status_col]
                
                row_line = self._create_data_row(row_with_status, temp_columns, border_chars)
            else:
                row_line = self._create_data_row(row_data, columns, border_chars)
            
            self.logger.info(row_line)
        
        # Create bottom border
        bottom_border = self._create_bottom_border(columns, border_chars)
        if bottom_border:
            self.logger.info(bottom_border)
        
        # Close title box if using unicode style
        if title and self.style == TableStyle.UNICODE:
            self.logger.info(f"╚{'═' * 84}╝")
    
    def log_summary_table(self,
                         title: str,
                         summary_data: Dict[str, Any],
                         value_formatter: Optional[Callable] = None) -> None:
        """
        Log a summary table with key-value pairs.
        
        Args:
            title: Table title
            summary_data: Dictionary of key-value pairs
            value_formatter: Optional formatter for values
        """
        if not summary_data:
            return
        
        # Create columns
        max_key_length = max(len(str(key)) for key in summary_data.keys())
        key_width = max(max_key_length + 2, 20)
        value_width = 30
        
        columns = [
            TableColumn("Item", key_width, "left"),
            TableColumn("Value", value_width, "right", value_formatter)
        ]
        
        # Convert to data rows
        data = [[key, value] for key, value in summary_data.items()]
        
        self.log_table(title, columns, data)
    
    def log_breakdown_table(self,
                           title: str,
                           breakdown_data: List[Dict[str, Any]],
                           key_column: str = "Item",
                           value_column: str = "Amount",
                           status_column: str = "Status") -> None:
        """
        Log a breakdown table with status indicators.
        
        Args:
            title: Table title
            breakdown_data: List of dictionaries with breakdown items
            key_column: Name for the key column
            value_column: Name for the value column
            status_column: Name for the status column
        """
        if not breakdown_data:
            return
        
        # Determine column widths
        max_key_length = max(len(str(item.get('key', ''))) for item in breakdown_data)
        key_width = max(max_key_length + 2, len(key_column) + 2, 25)
        value_width = 20
        status_width = 10
        
        columns = [
            TableColumn(key_column, key_width, "left"),
            TableColumn(value_column, value_width, "right"),
            TableColumn(status_column, status_width, "center")
        ]
        
        # Convert to data rows
        data = []
        for item in breakdown_data:
            key = item.get('key', '')
            value = item.get('value', 0)
            status = item.get('status', False)
            status_symbol = "✓" if status else "✗"
            data.append([key, value, status_symbol])
        
        self.log_table(title, columns, data)


# Convenience functions for common use cases
def log_taxation_breakdown(title: str, breakdown_items: List[Dict[str, Any]]) -> None:
    """Log taxation breakdown with standard formatting."""
    table_logger = TableLogger(TableStyle.UNICODE)
    table_logger.log_breakdown_table(title, breakdown_items)


def log_salary_summary(title: str, summary_data: Dict[str, Any]) -> None:
    """Log salary summary with standard formatting."""
    table_logger = TableLogger(TableStyle.UNICODE)
    table_logger.log_summary_table(title, summary_data)


def log_attendance_table(title: str, attendance_data: List[List[Any]], columns: List[TableColumn]) -> None:
    """Log attendance data with standard formatting."""
    table_logger = TableLogger(TableStyle.UNICODE)
    table_logger.log_table(title, columns, attendance_data)


def log_simple_table(title: str, data: List[List[Any]], headers: List[str]) -> None:
    """Log a simple table with basic headers."""
    columns = [TableColumn(header, 20, "left") for header in headers]
    table_logger = TableLogger(TableStyle.SIMPLE)
    table_logger.log_table(title, columns, data) 