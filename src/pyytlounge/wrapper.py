"""Wrapper class for YouTube Lounge API"""

import json
import logging
from enum import Enum
from typing import AsyncIterator, List

import aiohttp
from requests.models import PreparedRequest

from .api import api_base


async def __parse_event_chunks(lines: AsyncIterator[str]):
    chunk_remaining = 0
    current_chunk = ""
    async for line in lines:
        # todo: convert iterator at place of call
        if line is not str:
            line = line.decode()
        if chunk_remaining <= 0:
            chunk_remaining = int(line)
            current_chunk = ""
        else:
            current_chunk = current_chunk + line
            chunk_remaining = chunk_remaining - len(line) - 1
            if chunk_remaining == 0:
                events: List = json.loads(current_chunk)
                yield events


# useful for extending support
PRINT_UNKNOWN_EVENTS = False

# todo: replace with string enum with new python
class State(str, Enum):
    Stopped = ("-1",)
    Paused = ("1",)
    Playing = ("2",)
    Starting = ("3",)  # unsure, only seen once


class YtLoungeApi:
    """Wrapper class for YouTube Lounge API"""

    def __init__(self, device_name: str):
        self.device_name = device_name
        self.screen_id = None
        self.lounge_id_token = None
        self.sid = None
        self.gsession = None
        self.last_event_id = None

    def __paired(self):
        return self.screen_id is not None and self.lounge_id_token is not None

    def __connected(self):
        return self.sid is not None and self.gsession is not None

    def __repr__(self):
        return f"screen_id: {self.screen_id}\
                 lounge_id_token: {self.lounge_id_token}\
                 sid = {self.sid}\
                 gsession = {self.gsession}\
                 last_event_id = {self.last_event_id}\
                 "

    async def pair(self, pairing_code) -> bool:
        """Pair with a device using a manual input pairing code"""

        async with aiohttp.ClientSession() as session:
            pair_url = f"{api_base}/pairing/get_screen"
            pair_data = {"pairing_code": pairing_code}
            async with session.post(url=pair_url, data=pair_data) as resp:
                try:
                    screens = await resp.json()
                    screen = screens["screen"]
                    screen_name = screen["name"]
                    self.screen_id = screen["screenId"]
                    self.lounge_id_token = screen["loungeToken"]
                    return True
                except Exception as ex:
                    logging.exception(ex)
                    return False

    def load(self, screen_id: str, lounge_id_token: str):
        """Use the given screen id and lounge id token retrieved from manual pairing or discovery"""
        self.screen_id = screen_id
        self.lounge_id_token = lounge_id_token

    def __process_event(self, event_id: int, event_type: str, args):
        if event_type in ("onStateChange", "nowPlaying"):
            data = args[0]
            if "state" in data:
                state = State(data["state"])
                print(f"New state {state}")
        elif PRINT_UNKNOWN_EVENTS:
            print(f"{event_id} {event_type} {args}")

    def __process_events(self, events):
        sid, gsession = None, None
        for event in events:
            event_id, (event_type, *args) = event
            if event_type == "c":
                sid = args[0]
            elif event_type == "S":
                gsession = args[0]
            else:
                self.__process_event(event_id, event_type, args)

        last_id = events[-1][0]
        self.sid = sid
        self.gsession = gsession
        self.last_event_id = last_id

    async def connect(self) -> bool:
        """Attempt to connect using the previously set tokens"""
        if not self.__paired():
            raise Exception("Not paired")

        connect_body = {
            "app": "web",
            "mdx-version": "3",
            "name": self.device_name,
            "id": self.screen_id,
            "device": "REMOTE_CONTROL",
            "capabilities": "que,dsdtr,atp",
            "method": "setPlaylist",
            "magnaKey": "cloudPairedDevice",
            "ui": "",
            "deviceContext": "user_agent=dunno&window_width_points=&window_height_points=&os_name=android&ms=",
            "theme": "cl",
            "loungeIdToken": self.lounge_id_token,
        }
        connect_url = (
            f"{api_base}/bc/bind?RID=1&VER=8&CVER=1&auth_failure_option=send_error"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(connect_url, connect_body) as resp:
                try:
                    lines = await resp.text().splitlines()
                    async for events in __parse_event_chunks(lines):
                        self.__process_events(events)
                    return True
                except Exception as ex:
                    logging.exception(ex)
                    return False

    async def listen_events(self):
        """Start listening for events"""
        if not self.__connected():
            raise Exception("Not connected")

        print(f"Start listening with {self.sid}, {self.gsession}, {self.last_event_id}")
        params = {
            "device": "REMOTE_CONTROL",
            "name": self.device_name,
            "app": "youtube-desktop",
            "loungeIdToken": self.lounge_id_token,
            "VER": "8",
            "v": "2",
            "RID": "rpc",
            "SID": self.sid,
            "CI": "0",
            "AID": self.last_event_id,
            "gsessionid": self.gsession,
            "TYPE": "xmlhttp",
        }
        req = PreparedRequest()
        req.prepare_url(f"{api_base}/bc/bind", params)
        async with aiohttp.ClientSession() as session:
            async with session.get(req.url, stream=True) as resp:
                async for events in __parse_event_chunks(resp.iter_lines()):
                    self.__process_events(events)
