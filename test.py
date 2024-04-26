import asyncio
from src.pyytlounge.wrapper import YtLoungeApi, PlaybackState, State
from ast import literal_eval
import os
import logging

AUTH_STATE_FILE = "auth_state"
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

async def go():
    async with YtLoungeApi("Test", logger) as api:
        if os.path.exists(AUTH_STATE_FILE):
            with open(AUTH_STATE_FILE, "r") as f:
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
            with open(AUTH_STATE_FILE, "w") as f:
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

        last_video_id = None
        async def receive_state(state: PlaybackState):
            nonlocal last_video_id
            print(f"New state: {state}")
            if state.videoId and state.videoId != last_video_id:
                last_video_id = state.videoId
                print(
                    f"Image should be at: https://img.youtube.com/vi/{state.videoId}/0.jpg"
                )

        await api.subscribe(receive_state)


asyncio.run(go())
