from dataclasses import dataclass
from enum import Enum
import logging
from typing import Optional, TypedDict


class State(Enum):
    """Playback state"""

    Stopped = -1
    Buffering = 0  # unsure, happens between videos
    Playing = 1
    Paused = 2
    Starting = 3  # unsure, only seen once
    Advertisement = 1081


class _PlaybackStateData(TypedDict):
    """Representation of playback state as reported by API"""

    currentTime: str
    duration: str
    state: str


class _NowPlayingData(_PlaybackStateData):
    """Representation of now playing state as reported by API"""

    videoId: str


class PlaybackState:
    """Current playback state"""

    currentTime: float
    duration: float
    videoId: str
    state: State

    def __init__(self, logger: logging.Logger, state: Optional[_NowPlayingData] = None):
        self._logger = logger

        if not state or "state" not in state:
            self.currentTime = 0.0
            self.duration = 0.0
            self.videoId = ""
            self.state = State.Stopped
            return

        self.apply_state(state)
        self.videoId = state["videoId"]

    def apply_state(self, state: _PlaybackStateData):
        """Apply the new state on top of current state"""
        self.currentTime = float(state["currentTime"])
        self.duration = float(state["duration"])
        try:
            self.state = State(int(state["state"]))
        except ValueError:
            self._logger.warning(
                "Unknown state %s %s. Assuming stopped state.", state["state"], state
            )
            self.state = State.Stopped

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __repr__(self):
        return f"{self.state} - id: {self.videoId} pos: {self.currentTime} duration: {self.duration}"


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


class _DeviceInfo(TypedDict):
    brand: str
    model: str
    os: str


class _Device(TypedDict):
    name: str
    type: str
    id: str
    deviceInfo: str  # json string


class _LoungeStatus(TypedDict):
    devices: str  # json string containing list of __Device
