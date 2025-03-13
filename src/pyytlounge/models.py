from dataclasses import dataclass
from enum import Enum
import logging
from typing import TypedDict


_logger = logging.getLogger(__name__)


class State(Enum):
    """Playback state"""

    Stopped = -1
    Buffering = 0  # unsure, happens between videos
    Playing = 1
    Paused = 2
    Starting = 3  # unsure, only seen once
    Advertisement = 1081

    @staticmethod
    def parse(state: str) -> "State":
        """Parse a state value to State enum"""
        try:
            return State(int(state["state"]))
        except ValueError:
            _logger.warning("Unknown state %s %s. Assuming stopped state.", state["state"], state)
            return State.Stopped


CURRENT_AUTH_VERSION = 0


class AuthStateData(TypedDict):
    """Auth state in serialized state"""

    version: int
    screenId: str
    loungeIdToken: str
    refreshToken: str
    expiry: int


@dataclass
class AuthState:
    """Stores information used to authenticate with YouTube.
    Can be serialized and deserialized for reuse."""

    version: int
    screen_id: str
    lounge_id_token: str
    refresh_token: str
    expiry: int

    def __init__(self):
        super().__init__()
        self.version = CURRENT_AUTH_VERSION
        self.screen_id = None
        self.lounge_id_token = None
        self.refresh_token = None
        self.expiry = None

    def serialize(self) -> AuthStateData:
        """Serializes the current state into a dictionary."""
        return vars(self)

    def deserialize(self, data: AuthStateData):
        """Deserializes state from a dictionary into this object."""
        if data["version"] == CURRENT_AUTH_VERSION:
            for key in data:
                setattr(self, key, data[key])


class DpadCommand(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ENTER = "ENTER"
    BACK = "BACK"
