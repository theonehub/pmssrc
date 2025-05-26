"""
Working Hours Value Object
Handles time tracking, break calculations, and overtime logic
"""

from datetime import datetime, time, timedelta
from typing import Optional, List, Tuple
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TimeSlot:
    """Represents a time slot with start and end times"""
    start_time: datetime
    end_time: datetime
    
    def __post_init__(self):
        """Validate the time slot"""
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
    
    def duration_minutes(self) -> int:
        """Get duration in minutes"""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def duration_hours(self) -> Decimal:
        """Get duration in hours"""
        return Decimal(self.duration_minutes()) / Decimal(60)
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Check if this time slot overlaps with another"""
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)


@dataclass(frozen=True)
class WorkingHours:
    """
    Value object representing working hours for an attendance record.
    
    Follows SOLID principles:
    - SRP: Encapsulates working hours logic
    - OCP: Extensible through new calculation methods
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for time operations
    - DIP: Depends on abstractions (datetime)
    """
    
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    break_slots: List[TimeSlot] = None
    expected_hours: Decimal = Decimal("8.0")  # Standard 8-hour workday
    minimum_hours: Decimal = Decimal("4.0")   # Minimum for half day
    overtime_threshold: Decimal = Decimal("8.0")  # Overtime after 8 hours
    
    def __post_init__(self):
        """Validate working hours"""
        if self.break_slots is None:
            object.__setattr__(self, 'break_slots', [])
        
        if self.check_in_time and self.check_out_time:
            if self.check_in_time >= self.check_out_time:
                raise ValueError("Check-in time must be before check-out time")
        
        if self.expected_hours <= 0:
            raise ValueError("Expected hours must be positive")
        
        if self.minimum_hours <= 0:
            raise ValueError("Minimum hours must be positive")
        
        if self.overtime_threshold <= 0:
            raise ValueError("Overtime threshold must be positive")
        
        # Validate break slots don't overlap
        for i, slot1 in enumerate(self.break_slots):
            for j, slot2 in enumerate(self.break_slots[i+1:], i+1):
                if slot1.overlaps_with(slot2):
                    raise ValueError(f"Break slots {i} and {j} overlap")
    
    def is_checked_in(self) -> bool:
        """Check if employee has checked in"""
        return self.check_in_time is not None
    
    def is_checked_out(self) -> bool:
        """Check if employee has checked out"""
        return self.check_out_time is not None
    
    def is_complete_day(self) -> bool:
        """Check if both check-in and check-out are recorded"""
        return self.is_checked_in() and self.is_checked_out()
    
    def total_time_minutes(self) -> int:
        """Calculate total time spent in office (including breaks)"""
        if not self.is_complete_day():
            return 0
        
        return int((self.check_out_time - self.check_in_time).total_seconds() / 60)
    
    def break_time_minutes(self) -> int:
        """Calculate total break time in minutes"""
        if not self.break_slots:
            return 0
        
        total_break = 0
        for slot in self.break_slots:
            # Only count breaks that fall within working hours
            if (self.check_in_time and self.check_out_time and
                slot.start_time >= self.check_in_time and 
                slot.end_time <= self.check_out_time):
                total_break += slot.duration_minutes()
        
        return total_break
    
    def working_time_minutes(self) -> int:
        """Calculate actual working time (excluding breaks)"""
        return max(0, self.total_time_minutes() - self.break_time_minutes())
    
    def working_hours(self) -> Decimal:
        """Calculate working hours as decimal"""
        return Decimal(self.working_time_minutes()) / Decimal(60)
    
    def is_full_day(self) -> bool:
        """Check if working hours qualify as full day"""
        return self.working_hours() >= self.expected_hours
    
    def is_half_day(self) -> bool:
        """Check if working hours qualify as half day"""
        working_hrs = self.working_hours()
        return self.minimum_hours <= working_hrs < self.expected_hours
    
    def is_insufficient_hours(self) -> bool:
        """Check if working hours are insufficient"""
        return self.working_hours() < self.minimum_hours
    
    def overtime_hours(self) -> Decimal:
        """Calculate overtime hours"""
        working_hrs = self.working_hours()
        if working_hrs > self.overtime_threshold:
            return working_hrs - self.overtime_threshold
        return Decimal("0")
    
    def shortage_hours(self) -> Decimal:
        """Calculate shortage hours from expected"""
        working_hrs = self.working_hours()
        if working_hrs < self.expected_hours:
            return self.expected_hours - working_hrs
        return Decimal("0")
    
    def is_late_arrival(self, expected_start_time: time) -> bool:
        """Check if employee arrived late"""
        if not self.check_in_time:
            return False
        
        expected_datetime = datetime.combine(
            self.check_in_time.date(), 
            expected_start_time
        )
        return self.check_in_time > expected_datetime
    
    def late_arrival_minutes(self, expected_start_time: time) -> int:
        """Calculate late arrival in minutes"""
        if not self.is_late_arrival(expected_start_time):
            return 0
        
        expected_datetime = datetime.combine(
            self.check_in_time.date(), 
            expected_start_time
        )
        return int((self.check_in_time - expected_datetime).total_seconds() / 60)
    
    def is_early_departure(self, expected_end_time: time) -> bool:
        """Check if employee left early"""
        if not self.check_out_time:
            return False
        
        expected_datetime = datetime.combine(
            self.check_out_time.date(), 
            expected_end_time
        )
        return self.check_out_time < expected_datetime
    
    def early_departure_minutes(self, expected_end_time: time) -> int:
        """Calculate early departure in minutes"""
        if not self.is_early_departure(expected_end_time):
            return 0
        
        expected_datetime = datetime.combine(
            self.check_out_time.date(), 
            expected_end_time
        )
        return int((expected_datetime - self.check_out_time).total_seconds() / 60)
    
    def with_check_in(self, check_in_time: datetime) -> 'WorkingHours':
        """Create new working hours with check-in time"""
        return WorkingHours(
            check_in_time=check_in_time,
            check_out_time=self.check_out_time,
            break_slots=self.break_slots,
            expected_hours=self.expected_hours,
            minimum_hours=self.minimum_hours,
            overtime_threshold=self.overtime_threshold
        )
    
    def with_check_out(self, check_out_time: datetime) -> 'WorkingHours':
        """Create new working hours with check-out time"""
        return WorkingHours(
            check_in_time=self.check_in_time,
            check_out_time=check_out_time,
            break_slots=self.break_slots,
            expected_hours=self.expected_hours,
            minimum_hours=self.minimum_hours,
            overtime_threshold=self.overtime_threshold
        )
    
    def with_break(self, break_slot: TimeSlot) -> 'WorkingHours':
        """Create new working hours with additional break"""
        new_breaks = list(self.break_slots) + [break_slot]
        return WorkingHours(
            check_in_time=self.check_in_time,
            check_out_time=self.check_out_time,
            break_slots=new_breaks,
            expected_hours=self.expected_hours,
            minimum_hours=self.minimum_hours,
            overtime_threshold=self.overtime_threshold
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "check_in_time": self.check_in_time.isoformat() if self.check_in_time else None,
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
            "break_slots": [
                {
                    "start_time": slot.start_time.isoformat(),
                    "end_time": slot.end_time.isoformat()
                }
                for slot in self.break_slots
            ],
            "expected_hours": float(self.expected_hours),
            "minimum_hours": float(self.minimum_hours),
            "overtime_threshold": float(self.overtime_threshold),
            "working_hours": float(self.working_hours()),
            "overtime_hours": float(self.overtime_hours()),
            "shortage_hours": float(self.shortage_hours())
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WorkingHours':
        """Create from dictionary representation"""
        break_slots = []
        for slot_data in data.get("break_slots", []):
            break_slots.append(TimeSlot(
                start_time=datetime.fromisoformat(slot_data["start_time"]),
                end_time=datetime.fromisoformat(slot_data["end_time"])
            ))
        
        return cls(
            check_in_time=datetime.fromisoformat(data["check_in_time"]) if data.get("check_in_time") else None,
            check_out_time=datetime.fromisoformat(data["check_out_time"]) if data.get("check_out_time") else None,
            break_slots=break_slots,
            expected_hours=Decimal(str(data.get("expected_hours", "8.0"))),
            minimum_hours=Decimal(str(data.get("minimum_hours", "4.0"))),
            overtime_threshold=Decimal(str(data.get("overtime_threshold", "8.0")))
        )
    
    @classmethod
    def create_empty(cls, expected_hours: Decimal = Decimal("8.0")) -> 'WorkingHours':
        """Create empty working hours"""
        return cls(expected_hours=expected_hours)
    
    @classmethod
    def create_with_check_in(cls, check_in_time: datetime, expected_hours: Decimal = Decimal("8.0")) -> 'WorkingHours':
        """Create working hours with check-in"""
        return cls(
            check_in_time=check_in_time,
            expected_hours=expected_hours
        ) 