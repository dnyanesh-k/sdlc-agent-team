import uuid
from dataclasses import dataclass, Field
from pydantic import BaseModel

from enum import Enum

class SpeakerRole(str, Enum):
    PRODUCT_MANAGER = "Product Manager"
    DDEVELOPER = "Developer"

    
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
    feature_requests : str
    requirements : list[Requirement]
    code : CodeImplementation
    test_result : list[TestResult]
    current_phase : SprintPhase
    conversation_log : list[dict[str, str]]
    turn_count : int
    max_turns : int
    all_tests_passed : bool
    terminate : bool

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


    