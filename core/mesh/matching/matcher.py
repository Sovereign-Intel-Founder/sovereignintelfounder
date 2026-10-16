"""
Sovereign Intelligence Protocol - Job Matching & Scheduling
Evaluates task capability requirements against the capability index
and schedules execution dispatch.
"""

from typing import List, Optional
from dataclasses import dataclass, field
import time

@dataclass
class JobTask:
    task_id: str
    required_caps: List[str]
    payload_ref: str
    created_at: float = field(default_factory=time.time)


class JobMatcher:
    """
    Matches incoming jobs to qualified participants using the capability index.
    """
    def __init__(self, capability_index) -> None:
        self.index = capability_index

    def schedule_job(self, task: JobTask) -> Optional[str]:
        """
        Finds the optimal participant for a given task using capability intersection.
        Returns the selected participant_id or None if no match is found.
        """
        candidates = self.index.find_matching_participants(task.required_caps)
        if not candidates:
            return None
        
        # Deterministic selection policy: select the lexically first verified candidate
        return candidates[0]
