from dataclasses import dataclass
from datetime import date
from typing import Optional
from app.domain.value_objects.money import Money

@dataclass
class TDSStatus:
    """
    Represents a TDS status for a given month.
    """
    paid: bool
    month: int
    total_tax_liability: Money
    tds_challan_number: Optional[str] = None
    tds_challan_date: Optional[date] = None
    tds_challan_file_path: Optional[str] = None 


@dataclass
class PayoutStatus:
    """
    Represents a payout status for a given month.
    """
    status: str = 'computed'
    comments: Optional[str] = None
    transaction_id: Optional[str] = None
    transfer_date: Optional[date] = None