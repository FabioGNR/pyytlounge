import logging

from .api import get_thumbnail_url
from .models import State
from .lounge_models import (
    _NowPlayingData,
    _PlaybackStateData,
    _VolumeChangedData,
    _AutoplayModeChangedData,
    _AdStateData,
    _AdPlayingData,
    _SubtitlesTrackData,
    _AutoplayUpNextData,
    _PlaybackSpeedData,
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


class AdStateEvent:
    """Contains information related to ad state"""

    def __init__(self, data: _AdStateData):
        self.ad_state = State.parse(data["adState"])
        self.current_time: float = float(data["currentTime"])
        self.is_skip_enabled: bool = data["isSkipEnabled"] == "true"

class AdPlayingEvent:
    """Contains information related to ad state"""

    def __init__(self, data: _AdPlayingData):
        self.ad_video_id: str | None = data.get("adVideoId", None)
        self.ad_video_uri: str | None = data.get("adVideoUri", None)
        self.ad_title: str = data["adTitle"]
        self.is_bumper: bool = data["isBumper"] == "true"
        self.is_skippable: bool = data["isSkippable"] == "true"
        self.is_skip_enabled: bool = data["isSkipEnabled"] == "true"
        self.click_through_url: str = data["clickThroughUrl"]
        self.ad_system: str = data["adSystem"]
        self.ad_next_params: str = data["adNextParams"]
        self.remote_slots_data: str | None = data.get("remoteSlotsData", None)
        self.ad_state = State.parse(data["adState"])
        self.content_video_id: str = data["contentVideoId"]
        self.duration: float = float(data["duration"])
        self.current_time: float = float(data["currentTime"])


class SubtitlesTrackEvent:
    """Contains information related to subtitles track"""

    def __init__(self, data: _SubtitlesTrackData):
        self.video_id: str = data["videoId"]
        self.track_name: str | None = data.get("trackName", None)
        self.language_code: str | None = data.get("languageCode", None)
        self.source_language_code: str | None = data.get("sourceLanguageCode", None)
        self.language_name: str | None = data.get("languageName", None)
        self.kind: str | None = data.get("kind", None)
        self.vss_id: str | None = data.get("vss_id", None)
        self.caption_id: str | None = data.get("captionId", None)
        self.style: str | None = data.get("style", None)


class AutoplayUpNextEvent:
    """Contains information related the next video to be played"""

    def __init__(self, data: _AutoplayUpNextData):
        self.video_id: str = data["videoId"]


class PlaybackSpeedEvent:
    """Contains information related to playback speed"""

    def __init__(self, data: _PlaybackSpeedData):
        self.playback_speed: float = data["playbackSpeed"]
