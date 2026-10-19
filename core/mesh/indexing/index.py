"""
Sovereign Intelligence Protocol - Capability Indexing Layer
Maintains an in-memory/durable index of participant capabilities for 
low-latency mesh admission and job routing.
"""

from typing import Dict, List, Set, Optional
from core.mesh.registration.schema import ParticipantRegistration

class CapabilityIndex:
    """
    In-memory capability index mapping capability strings 
    to sets of registered participant identifiers.
    """
    def __init__(self) -> None:
        self._capability_map: Dict[str, Set[str]] = {}
        self._participants: Dict[str, ParticipantRegistration] = {}

    def register(self, registration: ParticipantRegistration) -> None:
        """Indexes a validated participant registration."""
        self._participants[registration.participant_id] = registration
        for cap in registration.supported_caps:
            if cap not in self._capability_map:
                self._capability_map[cap] = set()
            self._capability_map[cap].add(registration.participant_id)

    def unregister(self, participant_id: str) -> None:
        """Removes a participant and unlinks their capabilities from the index."""
        if participant_id in self._participants:
            reg = self._participants.pop(participant_id)
            for cap in reg.supported_caps:
                if cap in self._capability_map:
                    self._capability_map[cap].discard(participant_id)
                    if not self._capability_map[cap]:
                        del self._capability_map[cap]

    def find_matching_participants(self, required_caps: List[str]) -> List[str]:
        """
        Returns an intersection of participant IDs that satisfy 
        all requested capability requirements.
        """
        if not required_caps:
            return []

        matching_sets: List[Set[str]] = []
        for cap in required_caps:
            if cap not in self._capability_map:
                return [] # Capability not found anywhere in the mesh
            matching_sets.append(self._capability_map[cap])

        # Intersect sets to find participants possessing *all* requested capabilities
        intersection = set.intersection(*matching_sets)
        return sorted(list(intersection))

    def get_participant(self, participant_id: str) -> Optional[ParticipantRegistration]:
        return self._participants.get(participant_id)
