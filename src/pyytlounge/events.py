import logging

from .api import get_thumbnail_url
from .models import State
from .lounge_models import _NowPlayingData, _PlaybackStateData

_logger = logging.getLogger(__name__)


class PlaybackStateEvent:
    """Contains information related to playback state"""

    def __init__(self, data: _PlaybackStateData):
        self.current_time: float = float(data["currentTime"])
        self.duration: float = float(data["duration"])
        try:
            self.state = State(int(data["state"]))
        except ValueError:
            _logger.warning("Unknown state %s %s. Assuming stopped state.", data["state"], data)
            self.state = State.Stopped


class NowPlayingEvent(PlaybackStateEvent):
    """Contains information related to playback state"""

    def __init__(self, data: _NowPlayingData):
        super().__init__(data)
        self.video_id: str = data["videoId"]

    def get_thumbnail_url(self, thumbnail_idx: int = 0):
        """Returns thumbnail for current video. Use thumbnail idx to get different thumbnails."""

        get_thumbnail_url(self.video_id, thumbnail_idx=thumbnail_idx)
