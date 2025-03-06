from abc import ABC

from .events import NowPlayingEvent, PlaybackStateEvent


class EventListener(ABC):
    """Base class to implement an event listener"""

    def __init__(self):
        pass

    async def playback_state_changed(self, event: PlaybackStateEvent) -> None:
        """Called when playback state changes (position, play/pause)"""

    async def now_playing_changed(self, event: NowPlayingEvent) -> None:
        """Called when active video changes"""

    async def disconnected(self) -> None:
        """Called when the screen is no longer connected"""


class _EmptyListener(EventListener):
    """Empty listener which does nothing for convenience"""
