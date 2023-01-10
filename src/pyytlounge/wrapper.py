"""Wrapper class for YouTube Lounge API"""

import json
import logging
from enum import Enum
from typing import AsyncIterator, List, TypedDict, Union

import aiohttp
from aiohttp import ClientTimeout
from requests.models import PreparedRequest

from .api import api_base

# useful for extending support
PRINT_UNKNOWN_EVENTS = False


class State(Enum):
    Stopped = -1
    Playing = 1
    Paused = 2
    Starting = 3  # unsure, only seen once


class PlaybackStateData(TypedDict):
    currentTime: str
    duration: str
    state: str


class NowPlayingData(PlaybackStateData):
    videoId: str


class PlaybackState:
    currentTime: float
    duration: float
    videoId: str
    state: State

    def __init__(self, state: Union[NowPlayingData, None] = None):
        if not state or "state" not in state:
            self.currentTime = 0.0
            self.duration = 0.0
            self.videoId = ""
            self.state = State.Stopped
            return

        self.apply_state(state)
        self.videoId = state["videoId"]

    def apply_state(self, state: PlaybackStateData):
        self.currentTime = float(state["currentTime"])
        self.duration = float(state["duration"])
        self.state = State(int(state["state"]))

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __repr__(self):
        return f"{self.state} - id: {self.videoId} pos: {self.currentTime} duration: {self.duration}"


CURRENT_AUTH_VERSION = 0


class AuthStateData(TypedDict):
    version: int
    screenId: str
    loungeIdToken: str
    refreshToken: str
    expiry: int


class AuthState:
    version: int
    screen_id: str
    lounge_id_token: str
    refresh_token: str
    expiry: int

    def __init__(self):
        self.version = CURRENT_AUTH_VERSION

    def serialize(self) -> AuthStateData:
        return vars(self)

    def deserialize(self, data: AuthStateData):
        if data["version"] == CURRENT_AUTH_VERSION:
            for key in data:
                setattr(self, key, data[key])


async def desync(it):
    for x in it:
        yield x


async def iter_response_lines(resp):
    while True:
        line = await resp.readline()
        if line:
            yield line.decode()
        else:
            break


class YtLoungeApi:
    """Wrapper class for YouTube Lounge API"""

    def __init__(self, device_name: str):
        self.device_name = device_name
        self.auth = AuthState()
        self._sid = None
        self._gsession = None
        self._last_event_id = None
        self.state = PlaybackState()
        self.state_update = 0
        self._screen_name = None

    def __paired(self):
        return self.auth.screen_id is not None and self.auth.lounge_id_token is not None

    def __connected(self):
        return self._sid is not None and self._gsession is not None

    def __repr__(self):
        return f"screen_id: {self.auth.screen_id}\n\
                 lounge_id_token: {self.auth.lounge_id_token}\n\
                 sid = {self._sid}\n\
                 gsession = {self._gsession}\n\
                 last_event_id = {self._last_event_id}\n\
                 "

    @property
    def screen_name(self) -> str:
        """Returns screen name as returned by YouTube"""
        if not self.__paired():
            raise Exception("Not paired")

        return self._screen_name

    async def pair(self, pairing_code) -> bool:
        """Pair with a device using a manual input pairing code"""

        async with aiohttp.ClientSession() as session:
            pair_url = f"{api_base}/pairing/get_screen"
            pair_data = {"pairing_code": pairing_code}
            async with session.post(url=pair_url, data=pair_data) as resp:
                try:
                    screens = await resp.json()
                    screen = screens["screen"]
                    self._screen_name = screen["name"]
                    self.auth.screen_id = screen["screenId"]
                    self.auth.lounge_id_token = screen["loungeToken"]
                    return self.__paired()
                except Exception as ex:
                    logging.exception(ex)
                    return False

    def store_auth_state(self) -> dict:
        return {
            "screenId": self.auth.screen_id,
            "lounge_id_token": self.auth.lounge_id_token,
            "refresh_token": self.auth.refresh_token,
        }

    def load_auth_state(self, data: dict):
        self.auth = AuthState()
        self.auth.deserialize(data)

    def __update_state(self):
        self.state_update = self.state_update + 1

    def __process_event(self, event_id: int, event_type: str, args):
        if event_type == "onStateChange":
            data = args[0]
            self.state.apply_state(data)
            self.__update_state()
        elif event_type == "nowPlaying":
            data = args[0]
            self.state = PlaybackState(data)
            self.__update_state()
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
        self._sid = sid
        self._gsession = gsession
        self._last_event_id = last_id

    async def __parse_event_chunks(self, lines: AsyncIterator[str]):
        chunk_remaining = 0
        current_chunk = ""
        async for line in lines:
            if chunk_remaining <= 0:
                chunk_remaining = int(line)
                current_chunk = ""
            else:
                line = line.replace("\n", "")
                current_chunk = current_chunk + line
                chunk_remaining = chunk_remaining - len(line) - 1

                if chunk_remaining == 0:
                    events: List = json.loads(current_chunk)
                    yield events

    async def connect(self) -> bool:
        """Attempt to connect using the previously set tokens"""
        if not self.__paired():
            raise Exception("Not paired")

        connect_body = {
            "app": "web",
            "mdx-version": "3",
            "name": self.device_name,
            "id": self.auth.screen_id,
            "device": "REMOTE_CONTROL",
            "capabilities": "que,dsdtr,atp",
            "method": "setPlaylist",
            "magnaKey": "cloudPairedDevice",
            "ui": "",
            "deviceContext": "user_agent=dunno&window_width_points=&window_height_points=&os_name=android&ms=",
            "theme": "cl",
            "loungeIdToken": self.auth.lounge_id_token,
        }
        connect_url = (
            f"{api_base}/bc/bind?RID=1&VER=8&CVER=1&auth_failure_option=send_error"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(url=connect_url, data=connect_body) as resp:
                try:
                    text = await resp.text()
                    lines = text.splitlines()
                    async for events in self.__parse_event_chunks(desync(lines)):
                        self.__process_events(events)
                    return self.__connected()
                except Exception as ex:
                    logging.exception(ex)
                    return False

    async def listen_events(self) -> PlaybackState:
        """Start listening for events"""
        if not self.__connected():
            raise Exception("Not connected")

        print(
            f"Start listening with {self._sid}, {self._gsession}, {self._last_event_id}"
        )
        params = {
            "device": "REMOTE_CONTROL",
            "name": self.device_name,
            "app": "youtube-desktop",
            "loungeIdToken": self.auth.lounge_id_token,
            "VER": "8",
            "v": "2",
            "RID": "rpc",
            "SID": self._sid,
            "CI": "0",
            "AID": self._last_event_id,
            "gsessionid": self._gsession,
            "TYPE": "xmlhttp",
        }
        req = PreparedRequest()
        req.prepare_url(f"{api_base}/bc/bind", params)
        async with aiohttp.ClientSession(timeout=ClientTimeout()) as session:
            async with session.get(req.url) as resp:
                async for events in self.__parse_event_chunks(
                    iter_response_lines(resp.content)
                ):
                    pre_state_update = self.state_update
                    self.__process_events(events)
                    if pre_state_update != self.state_update:
                        yield self.state
