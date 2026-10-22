"""Script to test connecting to the same screen with two different devices simultaneously"""

import asyncio
from ast import literal_eval
import os
from src.pyytlounge import (
    YtLoungeApi,
    EventListener,
    NowPlayingEvent,
    State
)


AUTH_STATE_FILES = {
    "Device 1": "auth_state",
    "Device 2": "auth_state_2",
}


class DebugEventListener(EventListener):
    def __init__(self, name: str):
        self.name = name

    async def now_playing_changed(self, event: NowPlayingEvent) -> None:
        """Called when active video changes"""
        # Showing only playing events for brevity
        if event.state == State.Playing:
            print(
                f"[{self.name} Handler] {event.state} (pos: {event.current_time})"
            )


event = asyncio.Event()
async def go(device_name: str):
    print(f"[{device_name}] Starting test...")

    listener = DebugEventListener(device_name)
    async with YtLoungeApi(device_name, listener) as api:
        if os.path.exists(AUTH_STATE_FILES[device_name]):
            with open(AUTH_STATE_FILES[device_name], "r", encoding="utf-8") as f:
                content = f.read()
                api.load_auth_state(literal_eval(content))
        else:
            pairing_code = input(f"[{device_name}] Enter pairing code: ")
            assert await api.pair(pairing_code)
            auth_state = api.auth.serialize()
            with open(AUTH_STATE_FILES[device_name], "w", encoding="utf-8") as f:
                f.write(str(auth_state))

        assert await api.is_available()

        assert await api.connect()
        print(f"[{device_name}] Connected to device")

        assert await api.play_video("dQw4w9WgXcQ")

        # Trigger the next test to start
        event.set()

        await api.subscribe()

async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(go('Device 1'))

        # Wait for the first device to connect
        await event.wait()
        await asyncio.sleep(5)

        tg.create_task(go('Device 2'))

asyncio.run(main())
