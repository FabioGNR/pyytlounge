"""Wrapper class for YouTube Lounge API"""

import json
import logging
from enum import Enum
from typing import Any, AsyncIterator, List, TypedDict, Union, Callable
from dataclasses import dataclass

import aiohttp
from aiohttp import ClientTimeout, StreamReader, ClientPayloadError

from .api import api_base


class State(Enum):
    """Playback state"""

    Stopped = -1
    Buffering = 0  # unsure, happens between videos
    Playing = 1
    Paused = 2
    Starting = 3  # unsure, only seen once
    Advertisement = 1081


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

    def __init__(
        self, logger: logging.Logger, state: Union[NowPlayingData, None] = None
    ):
        self._logger = logger

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
        try:
            self.state = State(int(state["state"]))
        except ValueError:
            self._logger.warning(
                "Unknown state %s %s. Assuming stopped state.", state["state"], state
            )
            self.state = State.Stopped

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


@dataclass
class AuthState:
    """Stores information used to authenticate with YouTube.
    Can be serialized and deserialized for reuse."""

    version: int
    screen_id: str
    lounge_id_token: str
    refresh_token: str
    expiry: int

    def __init__(self):
        super().__init__()
        self.version = CURRENT_AUTH_VERSION
        self.screen_id = None
        self.lounge_id_token = None
        self.refresh_token = None
        self.expiry = None

    def serialize(self) -> AuthStateData:
        """Serializes the current state into a dictionary."""
        return vars(self)

    def deserialize(self, data: AuthStateData):
        """Deserializes state from a dictionary into this object."""
        if data["version"] == CURRENT_AUTH_VERSION:
            for key in data:
                setattr(self, key, data[key])


class __DeviceInfo(TypedDict):
    brand: str
    model: str
    os: str


class __Device(TypedDict):
    name: str
    type: str
    id: str
    deviceInfo: str  # json string


class __LoungeStatus(TypedDict):
    devices: str  # json string containing list of __Device


async def desync(iterator):
    """Turns a synchronous iterator into an asynchronous iterator"""
    for item in iterator:
        yield item


async def iter_response_lines(resp: StreamReader):
    """Enumerate lines in response one at a time."""
    while True:
        line = await resp.readline()
        if line:
            yield line.decode()
        else:
            break


def get_thumbnail_url(video_id: str, thumbnail_idx=0) -> str:
    """Returns thumbnail for given video. Use thumbnail idx to get different thumbnails."""
    return f"https://img.youtube.com/vi/{video_id}/{thumbnail_idx}.jpg"


class NotConnectedException(Exception):
    """This exception indicates an operation that failed due to an incorrect state.
    The operation requires that there is an active connection to the API.
    Use the connected() and connect() functions on YtLoungeApi."""


class NotPairedException(Exception):
    """This exception indicates an operation that failed due to an incorrect state.
    The operation requires that the API has been paired with a screen.
    Use the paired() and pair() functions on YtLoungeApi."""


class NotLinkedException(Exception):
    """This exception indicates an operation that failed due to an incorrect state.
    The operation requires that the API has been linked with a screen.
    Use the linked(), pair() and refresh_auth() functions on YtLoungeApi."""


class YtLoungeApi:
    """Wrapper class for YouTube Lounge API"""

    def __init__(self, device_name: str, logger: logging.Logger = None):
        self.device_name = device_name
        self.auth = AuthState()
        self._sid = None
        self._gsession = None
        self._last_event_id = None
        self.state = PlaybackState(logger)
        self.state_update = 0
        self._command_offset = 1
        self._screen_name: str = None
        self._device_info: __DeviceInfo = None
        self._logger = logger or logging.Logger(__package__, logging.DEBUG)
        self.conn = aiohttp.TCPConnector(ttl_dns_cache=300)
        self.session = aiohttp.ClientSession(connector=self.conn)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        await self.session.close()
        await self.conn.close()

    def paired(self) -> bool:
        """Returns true if screen id is known."""
        return self.auth.screen_id is not None

    def linked(self) -> bool:
        """Returns true if paired and lounge id token is known."""
        return self.paired() and self.auth.lounge_id_token is not None

    def connected(self) -> bool:
        """Returns true if the screen's session is connected."""
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
        if not self.linked():
            raise NotLinkedException("Not linked")

        return self._screen_name

    @property
    def screen_device_name(self) -> str:
        """Returns device name built from device info returned by YouTube"""
        if not self.connected():
            raise NotConnectedException("Not connected")
        brand = self._device_info["brand"]
        model = self._device_info["model"]
        return f"{brand} {model}"

    async def pair(self, pairing_code) -> bool:
        """Pair with a device using a manual input pairing code"""

        pair_url = f"{api_base}/pairing/get_screen"
        pair_data = {"pairing_code": pairing_code}
        async with self.session.post(url=pair_url, data=pair_data) as resp:
            try:
                screens = await resp.json()
                screen = screens["screen"]
                self._screen_name = screen["name"]
                self.auth.screen_id = screen["screenId"]
                self.auth.lounge_id_token = screen["loungeToken"]
                return self.linked()
            except:
                self._logger.exception("Pairing failed")
                raise

    async def refresh_auth(self) -> bool:
        """Refresh lounge token using stored refresh token."""
        if not self.paired():
            raise NotPairedException("Must be paired")

        refresh_url = f"{api_base}/pairing/get_lounge_token_batch"
        refresh_data = {"screen_ids": self.auth.screen_id}
        async with self.session.post(url=refresh_url, data=refresh_data) as resp:
            try:
                screens = await resp.json()
                screen = screens["screens"][0]
                self.auth.screen_id = screen["screenId"]
                self.auth.lounge_id_token = screen["loungeToken"]

                self._logger.info(
                    "Refreshed auth, lounge id token %s", self.auth.lounge_id_token
                )

                return self.linked()
            except:
                self._logger.exception("Refresh auth failed")
                raise

    def store_auth_state(self) -> dict:
        """Return auth parameters as dict which can be serialized for later use"""
        return {
            "screenId": self.auth.screen_id,
            "lounge_id_token": self.auth.lounge_id_token,
            "refresh_token": self.auth.refresh_token,
        }

    def load_auth_state(self, data: dict):
        """Use deserialized auth parameters"""
        self.auth = AuthState()
        self.auth.deserialize(data)

    def _update_state(self):
        self.state_update = self.state_update + 1

    def _lounge_token_expired(self):
        self.auth.lounge_id_token = None

    def _connection_lost(self):
        self._sid = None
        self._gsession = None
        self._last_event_id = None

    def _process_event(self, event_id: int, event_type: str, args):
        if event_type == "onStateChange":
            data = args[0]
            self.state.apply_state(data)
            self._update_state()
        elif event_type == "nowPlaying":
            data = args[0]
            self.state = PlaybackState(self._logger, data)
            self._update_state()
        elif event_type == "loungeStatus":
            data: __LoungeStatus = args[0]
            devices: List[__Device] = json.loads(data["devices"])
            for device in devices:
                if device["type"] == "LOUNGE_SCREEN":
                    self._screen_name = device["name"]
                    self._device_info = json.loads(device.get("deviceInfo", "null"))
                    break
        elif event_type == "loungeScreenDisconnected":
            self.state = PlaybackState(self._logger)
            self._update_state()
            self._connection_lost()
            self._lounge_token_expired()
        elif event_type == "noop":
            pass  # no-op
        else:
            self._logger.debug("Unprocessed event %s %s", event_type, args)

    def _process_events(self, events):
        for event in events:
            event_id, (event_type, *args) = event
            if event_type == "c":
                self._sid = args[0]
            elif event_type == "S":
                self._gsession = args[0]
            else:
                self._process_event(event_id, event_type, args)

        last_id = events[-1][0]
        self._last_event_id = last_id

    async def _parse_event_chunks(self, lines: AsyncIterator[str]):
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

    async def is_available(self) -> bool:
        """Asks YouTube API if the screen is available.
        Must be linked prior to this."""

        if not self.linked():
            raise NotConnectedException("Not connected")

        body = {"lounge_token": self.auth.lounge_id_token}

        url = f"{api_base}/pairing/get_screen_availability"

        result = await self.session.post(url=url, data=body)
        status = await result.json()
        if "screens" in status and len(status["screens"]) > 0:
            return status["screens"][0]["status"] == "online"

        return False

    def get_thumbnail_url(self, thumbnail_idx=0) -> str:
        """Returns thumbnail for current video. Use thumbnail idx to get different thumbnails.
        Returns None if no video is set."""
        if not self.state.videoId:
            return None
        return get_thumbnail_url(self.state.videoId, thumbnail_idx)

    async def connect(self) -> bool:
        """Attempt to connect using the previously set tokens"""
        if not self.linked():
            raise NotLinkedException("Not linked")

        connect_body = {
            "app": "web",
            "mdx-version": "3",
            "name": self.device_name,
            "id": self.auth.screen_id,
            "device": "REMOTE_CONTROL",
            "capabilities": "que,dsdtr,atp",
            "method": "setPlaylist",
            "magnaKey": "cloudPairedDevice",
            "ui": "false",
            "deviceContext": "user_agent=dunno&window_width_points=&window_height_points=&os_name=android&ms=",
            "theme": "cl",
            "loungeIdToken": self.auth.lounge_id_token,
        }
        connect_url = (
            f"{api_base}/bc/bind?RID=1&VER=8&CVER=1&auth_failure_option=send_error"
        )
        async with self.session.post(url=connect_url, data=connect_body) as resp:
            try:
                text = await resp.text()
                if resp.status == 401:
                    self._lounge_token_expired()
                    return False

                if resp.status != 200:
                    self._logger.warning(
                        "Unknown reply to connect %i %s", resp.status, resp.reason
                    )
                    return False
                lines = text.splitlines()
                async for events in self._parse_event_chunks(desync(lines)):
                    self._process_events(events)
                self._command_offset = 1
                return self.connected()
            except:
                self._logger.exception(
                    "Handle connect failed, status %s reason %s",
                    resp.status,
                    resp.reason,
                )
                raise

    def _handle_session_result(self, status_code: int, reason: str) -> bool:
        if status_code == 400 and "Unknown SID" in reason:
            self._connection_lost()
            return False
        if status_code == 410 and "Gone" in reason:
            self._connection_lost()
            return False
        if status_code == 401 and "Expired" in reason:
            self._connection_lost()
            self._lounge_token_expired()
            return False
        return True

    async def subscribe(self, callback: Callable[[PlaybackState], Any]) -> None:
        """Start listening for events"""
        if not self.connected():
            raise NotConnectedException("Not connected")

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
        url = f"{api_base}/bc/bind"
        self._logger.info("Subscribing to lounge id %s", self.auth.lounge_id_token)
        async with self.session.get(url=url, params=params, timeout=ClientTimeout()) as resp:
            try:
                if not self._handle_session_result(resp.status, resp.reason):
                    return

                async for events in self._parse_event_chunks(
                    iter_response_lines(resp.content)
                ):
                    pre_state_update = self.state_update
                    self._process_events(events)
                    if pre_state_update != self.state_update:
                        await callback(self.state)
                    if not self.connected():
                        break
                self._logger.info(
                    "Subscribe completed, status %i %s", resp.status, resp.reason
                )
            except ClientPayloadError:
                self._logger.exception(
                    "Handle subscribe payload error, status %s reason %s",
                    resp.status,
                    resp.reason
                )
            except:
                self._logger.exception(
                    "Handle subscribe failed, status %s reason %s",
                    resp.status,
                    resp.reason,
                )
                raise

    async def disconnect(self) -> bool:
        """Disconnect from the current session"""
        if not self.connected():
            raise NotConnectedException("Not connected")

        command_body = {
            "ui": "",
            "TYPE": "terminate",
            "clientDisconnectReason": "MDX_SESSION_DISCONNECT_REASON_DISCONNECTED_BY_USER",
        }
        params = {
            "device": "REMOTE_CONTROL",
            "name": self.device_name,
            "app": "youtube-desktop",
            "loungeIdToken": self.auth.lounge_id_token,
            "VER": "8",
            "v": "2",
            "CVER": "1",
            "RID": self._command_offset,
            "SID": self._sid,
            "AID": self._last_event_id,
            "gsessionid": self._gsession,
            "auth_failure_option": "send_error",
        }
        url = f"{api_base}/bc/bind"
        async with self.session.post(url=url, data=command_body, params=params) as resp:
            try:
                response_text = await resp.text()
                if not self._handle_session_result(resp.status, response_text):
                    return False
                resp.raise_for_status()
                return True
            except:
                self._logger.exception("Disconnect failed")
                raise

    async def _command(self, command: str, command_parameters: dict = None) -> bool:
        if not self.connected():
            raise NotConnectedException("Not connected")

        command_body = {"count": 1, "ofs": self._command_offset, "req0__sc": command}
        if command_parameters:
            for cmd_param in command_parameters:
                value = command_parameters[cmd_param]
                command_body[f"req0_{cmd_param}"] = value

        self._command_offset += 1
        params = {
            "device": "REMOTE_CONTROL",
            "name": self.device_name,
            "app": "youtube-desktop",
            "loungeIdToken": self.auth.lounge_id_token,
            "VER": "8",
            "v": "2",
            "RID": self._command_offset,
            "SID": self._sid,
            "AID": self._last_event_id,
            "gsessionid": self._gsession,
        }
        url = f"{api_base}/bc/bind"
        async with self.session.post(url=url, data=command_body, params=params) as resp:
            try:
                response_text = await resp.text()
                if not self._handle_session_result(resp.status, response_text):
                    return False
                resp.raise_for_status()
                return True
            except:
                self._logger.exception("Command failed")
                raise

    async def play(self) -> bool:
        """Sends play command to screen"""
        return await self._command("play")

    async def pause(self) -> bool:
        """Sends pause command to screen"""
        return await self._command("pause")

    async def previous(self) -> bool:
        """Sends previous command to screen"""
        return await self._command("previous")

    async def next(self) -> bool:
        """Sends next command to screen"""
        return await self._command("next")

    async def seek_to(self, time: float) -> bool:
        """Seek to given time (seconds)"""
        return await self._command("seekTo", {"newTime": time})

    async def skip_ad(self) -> bool:
        """Skips ad if possible"""
        return await self._command("skipAd")

    async def set_volume(self, volume: int) -> bool:
        """Sets volume to given value (0-100)"""
        return await self._command("setVolume", {"volume": volume})
