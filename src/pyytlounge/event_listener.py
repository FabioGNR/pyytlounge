from abc import ABC

from .events import (
    NowPlayingEvent,
    PlaybackStateEvent,
    VolumeChangedEvent,
    AutoplayModeChangedEvent,
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

    async def disconnected(self) -> None:
        """Called when the screen is no longer connected"""


class _EmptyListener(EventListener):
    """Empty listener which does nothing for convenience"""
