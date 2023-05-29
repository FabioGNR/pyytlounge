#!/usr/bin/env python

import asyncio
import aiohttp
from api import api_base
async def get_screen(pairing_code):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_base}/pairing/get_screen", data={'pairing_code': pairing_code}) as response:
            return await response.json()
pairing_code = input("Enter manual pairing code as shown in YouTube app on target: ")
try:
    pairing_code = int(pairing_code)
except Exception as ex:
    print(f"Invalid pairing code {pairing_code}", ex)

# initial paring with code
loop = asyncio.get_event_loop()

screens = loop.run_until_complete(get_screen(pairing_code))
screen = screens["screen"]
screen_name = screen["name"]
screen_id = screen["screenId"]
lounge_token = screen["loungeToken"]

print(f"Found \"{screen_name}\" with id: '{screen_id}' token: '{lounge_token}'")

# refresh pairing from code
# res = requests.post(f"{api_base}/pairing/get_lounge_token_batch", data={'screen_ids': screen_id})

# print(f"Screen name {screen_name}, id: {screen_id}")
