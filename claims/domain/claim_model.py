from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import datetime

class ClaimPriority(str, Enum):
    URGENT = "URGENT" 
    MEDIUM = "MEDIUM"   
    LOW = "LOW"  

class ClaimCategory(str, Enum):
    INFRASTRUCTURE_DANGER = "INFRASTRUCTURE_DANGER"
    OUTAGE = "OUTAGE"                              
    BILLING = "BILLING"                           
    RECONNECTION = "RECONNECTION"                

class ClaimStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"  

@dataclass(frozen=True)
class ClaimModel:
    claim_id: str
    description: str
    category: ClaimCategory
    priority: ClaimPriority = ClaimPriority.MEDIUM
    status: ClaimStatus = ClaimStatus.OPEN
    
    service_number: Optional[str] = None   
    address: Optional[str] = None         
    billing_number: Optional[str] = None
    photos_url: Optional[str] = None
    
    created_at: datetime = field(default_factory=lambda: datetime.now(datetime.timezone.utc))



