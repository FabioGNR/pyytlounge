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
    api = YtLoungeApi("Test", logger)
    api.auth.screen_id = 'qofgtvoflsm72sc34jgfsue6ki'
    
    async with api:
        refreshed = await api.refresh_auth()
        if refreshed:
            print("Refreshed, now lounge id", api.auth.lounge_id_token)
        else:
            print("Refresh failed")


asyncio.run(go())
