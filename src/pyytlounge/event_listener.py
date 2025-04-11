from abc import ABC

from .events import (
    NowPlayingEvent,
    PlaybackStateEvent,
    VolumeChangedEvent,
    AutoplayModeChangedEvent,
    AdStateEvent,
    AdPlayingEvent,
    SubtitlesTrackEvent,
    AutoplayUpNextEvent,
    PlaybackSpeedEvent,
    DisconnectedEvent,
)


class EventListener(ABC):
    """Base class to implement an event listener.
    You should subclass this and override methods for events you're interested in."""

    def __init__(self):
        pass

    async def playback_state_changed(self, event: PlaybackStateEvent) -> None:
        """Called when playback state changes (position, play/pause)"""

    async def now_playing_changed(self, event: NowPlayingEvent) -> None:
        """Called when active video changes"""

    async def volume_changed(self, event: VolumeChangedEvent) -> None:
        """Called when volume or muted state changes"""

    async def autoplay_changed(self, event: AutoplayModeChangedEvent) -> None:
        """Called when auto play mode changes"""

    async def ad_state_changed(self, event: AdStateEvent) -> None:
        """Called when ad state changes (position, play/pause, skippable)"""

    async def ad_playing_changed(self, event: AdPlayingEvent) -> None:
        """Called when ad starts playing"""

    async def subtitles_track_changed(self, event: SubtitlesTrackEvent) -> None:
        """Called when subtitles track changes"""

    async def autoplay_up_next_changed(self, event: AutoplayUpNextEvent) -> None:
        """Called when up next video changes"""

    async def playback_speed_changed(self, event: PlaybackSpeedEvent) -> None:
        """Called when playback speed changes"""

    async def disconnected(self, event: DisconnectedEvent) -> None:
        """Called when the screen is no longer connected"""


class _EmptyListener(EventListener):
    """Empty listener which does nothing for convenience"""
