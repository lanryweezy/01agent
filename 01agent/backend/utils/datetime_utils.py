import datetime
from typing import Optional

def utc_now() -> datetime.datetime:
    """Return current UTC datetime with timezone info."""
    return datetime.datetime.now(datetime.timezone.utc)

def to_utc(dt: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
    """Convert datetime to UTC if it has timezone info, otherwise assume UTC."""
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        return dt.replace(tzinfo=datetime.timezone.utc)
    
    return dt.astimezone(datetime.timezone.utc)

def from_timestamp(timestamp: float) -> datetime.datetime:
    """Convert Unix timestamp to UTC datetime."""
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)