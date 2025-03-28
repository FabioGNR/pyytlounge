import logging

from .api import get_thumbnail_url
from .models import State
from .lounge_models import (
    _NowPlayingData,
    _PlaybackStateData,
    _VolumeChangedData,
    _AutoplayModeChangedData,
)

_logger = logging.getLogger(__name__)


class PlaybackStateEvent:
    """Contains information related to playback state"""

    def __init__(self, data: _PlaybackStateData):
        self.current_time: float = float(data["currentTime"])
        self.duration: float = float(data["duration"])
        self.state = State.parse(data["state"])


class NowPlayingEvent:
    """Contains information related to playback state"""

    def __init__(self, data: _NowPlayingData):
        self.video_id: str | None = data.get("videoId", None)
        self.current_time: float | None = (
            float(data["currentTime"]) if "currentTime" in data else None
        )
        self.duration: float | None = float(data["duration"]) if "duration" in data else None
        self.state = State.parse(data["state"]) if "state" in data else State.Stopped

    def get_thumbnail_url(self, thumbnail_idx: int = 0):
        """Returns thumbnail for current video. Use thumbnail idx to get different thumbnails."""

        get_thumbnail_url(self.video_id, thumbnail_idx=thumbnail_idx)


class VolumeChangedEvent:
    """Contains information related to volume"""

    def __init__(self, data: _VolumeChangedData):
        self.volume: int = data["volume"]
        self.muted: bool = data["muted"] == "true"


class AutoplayModeChangedEvent:
    """Contains auto play mode"""

    def __init__(self, data: _AutoplayModeChangedData):
        self.enabled: bool = data["autoplayMode"] == "ENABLED"
        self.supported: bool = data["autoplayMode"] != "UNSUPPORTED"
