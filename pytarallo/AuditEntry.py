from enum import Enum
from typing import Optional


class AuditChanges(Enum):
    Create = 'C'
    Update = 'U'
    Delete = 'D'
    Move = 'M'
    Lose = 'L'
    Rename = 'R'
    Unknown = '?'


class AuditEntry:
    def __init__(self, user: str, change: AuditChanges, time: float, other: Optional[str] = None):
        self.user = user
        self.change = change
        self.time = time
        self.other = other
