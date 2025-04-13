"""Script to test the API client with a screen"""

import asyncio
from ast import literal_eval
import os
import logging
from typing import Optional
from src.pyytlounge import (
    YtLoungeApi,
    EventListener,
    PlaybackStateEvent,
    NowPlayingEvent,
    VolumeChangedEvent,
    AutoplayModeChangedEvent,
    DisconnectedEvent,
    PlaybackSpeedEvent,
)

AUTH_STATE_FILE = "auth_state"
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


class DebugEventListener(EventListener):
    def __init__(self):
        self.last_video_id: Optional[str] = None

    async def playback_state_changed(self, event: PlaybackStateEvent) -> None:
        """Called when playback state changes (position, play/pause)"""
        print(
            f"New state: {event.state} = id: {self.last_video_id} pos: {event.current_time} duration: {event.duration}"
        )

    async def now_playing_changed(self, event: NowPlayingEvent) -> None:
        """Called when active video changes"""
        print(
            f"New state: {event.state} = id: {event.video_id} pos: {event.current_time} duration: {event.duration}"
        )
        if event.video_id and event.video_id != self.last_video_id:
            print(f"Image should be at: {event.get_thumbnail_url()}")
        self.last_video_id = event.video_id

    async def volume_changed(self, event: VolumeChangedEvent) -> None:
        """Called when volume or muted state changes"""
        print(f"Volume changed: {event.volume}% muted: {event.muted}")

    async def autoplay_changed(self, event: AutoplayModeChangedEvent) -> None:
        """Called when auto play mode changes"""
        print(
            f"Auto play changed: {event.enabled} {'(not supported)' if not event.supported else ''}"
        )

    async def playback_speed_changed(self, event: PlaybackSpeedEvent) -> None:
        """Called when playback speed changes"""
        print(f"Playback speed changed: {event.playback_speed}")

    async def disconnected(self, event: DisconnectedEvent) -> None:
        """Called when the screen is no longer connected"""
        print("Disconnected", event.reason)
        self.last_video_id = None


async def go():
    listener = DebugEventListener()
    async with YtLoungeApi("Test", listener, logger) as api:
        if os.path.exists(AUTH_STATE_FILE):
            with open(AUTH_STATE_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                api.load_auth_state(literal_eval(content))
                print("Loaded from file")
        else:
            pairing_code = input("Enter pairing code: ")
            print(f"Pairing with code {pairing_code}...")
            paired = await api.pair(pairing_code)
            print(paired and "success" or "failed")
            if not paired:
                exit()
            auth_state = api.auth.serialize()
            with open(AUTH_STATE_FILE, "w", encoding="utf-8") as f:
                f.write(str(auth_state))
        print(api)
        is_available = await api.is_available()
        print(f"Screen availability: {is_available}")

        print("Connecting...")
        connected = await api.connect()
        print(connected and "success" or "failed")
        if not connected:
            exit()

        print(f"Screen: {api.screen_name}")
        print(f"Device: {api.screen_device_name}")

        await api.play_video("dQw4w9WgXcQ")

        await api.subscribe()


asyncio.run(go())
