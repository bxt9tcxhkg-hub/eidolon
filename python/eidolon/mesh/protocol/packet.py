from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal
import uuid
import json


@dataclass
class EidolonPacket:
    version: int = 1
    packet_type: Literal[
        "device_hello",
        "device_goodbye",
        "device_heartbeat",
        "device_capability",
        "task_request",
        "task_response",
        "task_progress",
        "task_cancel",
        "chat_message",
        "voice_frame",
        "media_frame",
        "device_announce",
        "service_query",
        "service_response",
        "agent_hello",
        "agent_capability",
        "agent_task_request",
        "agent_task_response",
    ] = "device_announce"
    source: str = ""
    destination: str = ""
    payload: bytes = b""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def encode(self) -> bytes:
        return json.dumps(self.__dict__, default=str).encode("utf-8")

    @classmethod
    def decode(cls, data: bytes) -> EidolonPacket:
        obj = json.loads(data.decode("utf-8"))
        return cls(**obj)
