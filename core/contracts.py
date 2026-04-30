"""SPEACE Core — Common Operational Language and Execution Contracts."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import time
import uuid


class MessageType(Enum):
    COMMAND = "command"
    QUERY = "query"
    EVENT = "event"
    RESPONSE = "response"
    STATE_UPDATE = "state_update"
    ERROR = "error"


@dataclass
class SPEACEMessage:
    """Standard inter-module message."""
    sender: str
    receiver: str
    message_type: MessageType
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    correlation_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
        }


@dataclass
class ExecutionContract:
    """Validates pre-conditions, post-conditions, and invariants for graph node execution."""
    pre_conditions: list[Callable[[dict], bool]] = field(default_factory=list)
    post_conditions: list[Callable[[dict], bool]] = field(default_factory=list)
    invariants: list[Callable[[dict], bool]] = field(default_factory=list)
    timeout_seconds: float = 30.0
    required_capabilities: list[str] = field(default_factory=list)
    priority: int = 5  # 1-10, higher = more important

    def validate_pre(self, inputs: dict) -> tuple[bool, list[str]]:
        failures = [str(cond) for cond in self.pre_conditions if not cond(inputs)]
        return len(failures) == 0, failures

    def validate_post(self, outputs: dict) -> tuple[bool, list[str]]:
        failures = [str(cond) for cond in self.post_conditions if not cond(outputs)]
        return len(failures) == 0, failures

    def validate_invariants(self, state: dict) -> tuple[bool, list[str]]:
        failures = [str(inv) for inv in self.invariants if not inv(state)]
        return len(failures) == 0, failures


@dataclass
class NodeContract:
    """Typed input/output specification for a graph node."""
    input_types: dict[str, type] = field(default_factory=dict)
    output_types: dict[str, type] = field(default_factory=dict)
    pre_conditions: list[Callable[[dict], bool]] = field(default_factory=list)
    post_conditions: list[Callable[[dict], bool]] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


class CommonOperationalLanguage:
    """Factory for typed inter-module messages."""

    @staticmethod
    def create_command(sender: str, receiver: str, action: str, **kwargs) -> SPEACEMessage:
        return SPEACEMessage(
            sender=sender,
            receiver=receiver,
            message_type=MessageType.COMMAND,
            payload={"action": action, **kwargs},
        )

    @staticmethod
    def create_event(sender: str, event_type: str, **kwargs) -> SPEACEMessage:
        return SPEACEMessage(
            sender=sender,
            receiver="event_bus",
            message_type=MessageType.EVENT,
            payload={"event_type": event_type, **kwargs},
        )

    @staticmethod
    def create_response(sender: str, receiver: str, correlation_id: str, **kwargs) -> SPEACEMessage:
        return SPEACEMessage(
            sender=sender,
            receiver=receiver,
            message_type=MessageType.RESPONSE,
            payload=kwargs,
            correlation_id=correlation_id,
        )
