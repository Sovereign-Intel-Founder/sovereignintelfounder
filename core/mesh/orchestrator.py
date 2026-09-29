"""
Sovereign Intelligence Protocol - Stateless Execution Pipeline
Ties registration, indexing, matching, and evidence verification 
together into a deterministic, zero-overhead transaction boundary.
"""

from typing import Dict, Any, Optional
from core.mesh.matching.matcher import JobTask, JobMatcher
from core.mesh.execution.verifier import EvidenceReturn

class MeshPipeline:
    """
    Stateless pipeline controller. Executes local orchestration 
    strictly on-demand with zero persistent server footprint.
    """
    def __init__(self, capability_index) -> None:
        self.index = capability_index
        self.matcher = JobMatcher(self.index)

    def dispatch_and_verify(self, task: JobTask, evidence: EvidenceReturn) -> bool:
        """
        Executes an atomic dispatch check and verifies the resulting cryptographic evidence.
        Returns True if the worker was validly matched and the evidence integrity passes.
        """
        # Step 1: Ensure task matches an authorized, capable participant
        assigned_node = self.matcher.schedule_job(task)
        if not assigned_node:
            return False

        # Step 2: Ensure the evidence return originated from the assigned node
        if evidence.participant_id != assigned_node:
            return False

        # Step 3: Cryptographically verify output payload integrity
        return evidence.verify_integrity()
