from dataclasses import dataclass
from enum import Enum
import logging
from typing import TypedDict, cast


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
            return State(int(state))
        except ValueError:
            _logger.warning("Unknown state %s. Assuming stopped state.", state)
            return State.Stopped


AUTH_VERSION_V1 = 0
CURRENT_AUTH_VERSION = AUTH_VERSION_V1


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
        return AuthStateData(
            version=self.version,
            screenId=self.screen_id,
            loungeIdToken=self.lounge_id_token,
            refreshToken=self.refresh_token,
            expiry=self.expiry,
        )

    def deserialize(self, data: dict):
        """Deserializes state from a dictionary into this object."""
        if data["version"] == AUTH_VERSION_V1:
            v1_data: AuthStateData = cast(AuthStateData, data)
            self.version = v1_data["version"]
            self.screen_id = v1_data["screenId"]
            self.lounge_id_token = v1_data["loungeIdToken"]
            self.refresh_token = v1_data["refreshToken"]
            self.expiry = v1_data["expiry"]
        else:
            raise ValueError("Unknown authentication data version")


class DpadCommand(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ENTER = "ENTER"
    BACK = "BACK"


BLACKLISTED_CLIENTS = ["TVHTML5_FOR_KIDS"]
