import uuid
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from enum import Enum

class SpeakerRole(str, Enum):
    PRODUCT_MANAGER = "Product Manager"
    DEVELOPER = "Developer"

    
class SprintPhase(str, Enum):
    REQUIREMENTS = "requirements"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DONE = "done"


class Requirement(BaseModel):
    id: str = Field(default_factory=lambda: f"REQ-{uuid.uuid4().hex[:12].upper()}")
    title : str
    description : str
    acceptance_criteria : list[str] = Field(default_factory=list)
    priority : str = "medium"


class CodeImplementation(BaseModel):
    files : dict[str, str]
    description : str
    dependencies : list[str]


class TestResult(BaseModel):
    test_file : str
    passed : bool
    total_tests : int
    failure : int
    errors : int
    output : str


# dataclass - Automatically builds helper functions (called dunder methods) like __init__ (to create objects) and __repr__ (to print objects) behind the scenes.
# used on DTOs, API responses,
@dataclass
class GroupChatContext:
    feature_requests : str = ""
    requirements : list[Requirement] = field(default_factory=list)
    code : CodeImplementation = field(default_factory=CodeImplementation)
    test_result : list[TestResult] = field(default_factory=list)
    current_phase : SprintPhase = SprintPhase.REQUIREMENTS
    conversation_log : list[dict[str, str]] = field(default_factory=list)
    turn_count : int = 0
    max_turns : int = 30
    all_tests_passed : bool = False
    terminate : bool = False

    def log(self, speaker: SpeakerRole, message: str) -> None:
        self.conversation_log.append({
            "turn": str(self.turn_count),
            "speaker": speaker.value,
            "message": message
        })

    def summary(self) -> str:
        lines = [
            f"Feature: {self.feature_requests}",
            f"Phase: {self.current_phase.value}",
            f"Turn: {self.turn_count}/ {self.max_turns}",
            f"Test Passed: {self.all_tests_passed}",
            "",
            "---- Conversation Log ----"
        ]

        for entry in self.conversation_log:
            lines.append(
                f"[Turn {entry['turn']}] {entry['speaker']}: "
                f"{entry['message'][:200]}"
            )

            return "\n".join(lines)


    