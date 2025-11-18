# c:/Users/dbmar/Downloads/ai_planner/backend/models/mission.py
import uuid
from enum import Enum
from typing import List, Dict, Any

class MissionStatus(Enum):
    """Defines the possible states of a mission."""
    PENDING = "PENDING"
    CLARIFYING = "CLARIFYING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    REPORTING = "REPORTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Mission:
    """
    Represents the state and data of a single AI mission.
    This is the 'Model' in our MVC architecture.
    """
    def __init__(self, goal: str):
        self.id: str = str(uuid.uuid4())
        self.goal: str = goal
        self.status: MissionStatus = MissionStatus.PENDING
        self.plan: List[str] = []
        self.logs: List[Dict[str, Any]] = []
        self.report: str = ""
        self.clarified_goal: str = ""

    def add_log(self, message: str, node: str, data: Dict[str, Any] = None):
        """Adds a structured log entry."""
        self.logs.append({"message": message, "node": node, "data": data or {}})

    def set_status(self, status: MissionStatus):
        """Updates the mission status."""
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the mission object to a dictionary for API responses."""
        return {
            "id": self.id,
            "goal": self.goal,
            "status": self.status.value,
            "plan": self.plan,
            "report": self.report,
        }