import asyncio
from src.pyytlounge.wrapper import YtLoungeApi, PlaybackState, State
from ast import literal_eval
import os

AUTH_STATE_FILE = "auth_state"


async def go():
    api = YtLoungeApi("Test")
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

    async def receive_state(state: PlaybackState):
        print(f"New state: {state}")
        if state.videoId:
            print(
                f"Image should be at: https://img.youtube.com/vi/{state.videoId}/0.jpg"
            )

    await api.subscribe(receive_state)


asyncio.run(go())
