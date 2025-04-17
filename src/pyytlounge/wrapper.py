"""Wrapper class for YouTube Lounge API"""

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

import aiohttp
from aiohttp import ClientTimeout, ClientPayloadError

from .api import api_base
from .api import get_thumbnail_url, get_available_captions  # noqa # we want to export this from this module
from .event_listener import EventListener, _EmptyListener
from .events import (
    PlaybackStateEvent,
    NowPlayingEvent,
    VolumeChangedEvent,
    AutoplayModeChangedEvent,
    AdStateEvent,
    AdPlayingEvent,
    SubtitlesTrackEvent,
    AutoplayUpNextEvent,
    PlaybackSpeedEvent,
    DisconnectedEvent,
)
from .models import AuthState, DpadCommand, BLACKLISTED_CLIENTS
from .lounge_models import _Device, _DeviceInfo, _LoungeStatus
from .exceptions import (
    NotConnectedException,
    NotLinkedException,
    NotPairedException,
    NotSupportedException,
)
from .util import as_aiter, iter_response_lines


class YtLoungeApi:
    """YouTube Lounge API"""

    def __init__(
        self,
        device_name: str,
        event_listener: Optional[EventListener] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Create an instance of the API which can connect to a single screen

        :param device_name: This name will show up on the screen
        :param event_listener: Setting a listener allows you to receive updates from the screen
        :param logger: Override the logger with something custom
        """
        self.device_name = device_name
        self.auth = AuthState()
        self._sid = None
        self._gsession = None
        self._last_event_id = None
        self.event_listener = event_listener or _EmptyListener()
        self._command_offset = 1
        self._screen_name: Optional[str] = None
        self._device_info: Optional[_DeviceInfo] = None
        self._logger = logger or logging.Logger(__package__, logging.DEBUG)
        # Initialize these as None - they'll be set up in __aenter__
        self.conn: Optional[aiohttp.TCPConnector] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        try:
            self.conn = aiohttp.TCPConnector(ttl_dns_cache=300)
            self.session = aiohttp.ClientSession(connector=self.conn)
            return self
        except Exception:
            await self.close()
            raise

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        await self.session.close()
        await self.conn.close()

    @property
    def _required_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            raise RuntimeError("API is not initialized. Use async context manager.")
        return self.session

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
    def screen_name(self) -> Optional[str]:
        """Returns screen name as returned by YouTube.

        :raises NotLinkedException: there is no screen linked yet
        """
        if not self.linked():
            raise NotLinkedException("Not linked")

        return self._screen_name

    @property
    def screen_device_name(self) -> Optional[str]:
        """Returns device name built from device info returned by YouTube.
        Returns None if not yet initialized or information was not sent.

        :raises NotConnectedException: screen is not yet connected
        """
        if not self.connected():
            raise NotConnectedException("Not connected")
        if not self._device_info:
            return None
        brand = self._device_info["brand"]
        model = self._device_info["model"]
        return f"{brand} {model}"

    async def pair_with_screen_id(self, screen_id: str, screen_name: Optional[str] = None) -> bool:
        """Pair with a device using a known screen id
        Optionally specify the screen name if already known"""
        self.auth.screen_id = screen_id
        self._screen_name = screen_name
        return await self.refresh_auth()

    async def pair(self, pairing_code: str) -> bool:
        """Pair with a device using a manual input pairing code"""

        pair_url = f"{api_base}/pairing/get_screen"
        pair_data = {"pairing_code": pairing_code}
        async with self._required_session.post(url=pair_url, data=pair_data) as resp:
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
        """Refresh lounge token using stored refresh token.

        :raises NotPairedException: the screen is not yet known, pair first
        """
        if not self.paired():
            raise NotPairedException("Must be paired")

        refresh_url = f"{api_base}/pairing/get_lounge_token_batch"
        refresh_data = {"screen_ids": self.auth.screen_id}
        async with self._required_session.post(url=refresh_url, data=refresh_data) as resp:
            try:
                screens = await resp.json()
                screen = screens["screens"][0]
                self.auth.screen_id = screen["screenId"]
                self.auth.lounge_id_token = screen["loungeToken"]

                self._logger.info("Refreshed auth, lounge id token %s", self.auth.lounge_id_token)

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

    def _lounge_token_expired(self):
        self.auth.lounge_id_token = None

    def _connection_lost(self):
        self._sid = None
        self._gsession = None
        self._last_event_id = None

    async def _process_event(self, event_type: str, args: List[Any]):
        if event_type == "onStateChange" and self.event_listener:
            await self.event_listener.playback_state_changed(PlaybackStateEvent(args[0]))
        elif event_type == "nowPlaying":
            await self.event_listener.now_playing_changed(NowPlayingEvent(args[0]))
        elif event_type == "onVolumeChanged":
            await self.event_listener.volume_changed(VolumeChangedEvent(args[0]))
        elif event_type == "onAutoplayModeChanged":
            await self.event_listener.autoplay_changed(AutoplayModeChangedEvent(args[0]))
        elif event_type == "onAdStateChange":
            await self.event_listener.ad_state_changed(AdStateEvent(args[0]))
        elif event_type == "adPlaying":
            await self.event_listener.ad_playing_changed(AdPlayingEvent(args[0]))
        elif event_type == "onSubtitlesTrackChanged":
            await self.event_listener.subtitles_track_changed(SubtitlesTrackEvent(args[0]))
        elif event_type == "autoplayUpNext" and args:
            await self.event_listener.autoplay_up_next_changed(AutoplayUpNextEvent(args[0]))
        elif event_type == "onPlaybackSpeedChanged":
            await self.event_listener.playback_speed_changed(PlaybackSpeedEvent(args[0]))
            await self.get_now_playing()
        elif event_type == "loungeStatus":
            data: _LoungeStatus = args[0]
            devices: List[_Device] = json.loads(data["devices"])
            for device in devices:
                if device["type"] == "LOUNGE_SCREEN":
                    self._screen_name = device["name"]
                    self._device_info = json.loads(device.get("deviceInfo", "null"))
                    if (
                        self._device_info
                        and self._device_info.get("clientName", "") in BLACKLISTED_CLIENTS
                    ):
                        raise NotSupportedException("Unsupported client")
                    break
        elif event_type == "loungeScreenDisconnected":
            await self.event_listener.disconnected(DisconnectedEvent(args[0] if args else None))
            self._connection_lost()
            self._lounge_token_expired()
        elif event_type == "noop":
            pass  # no-op
        else:
            self._logger.debug("Unprocessed event %s %s", event_type, args)

    async def _process_events(self, events):
        for event in events:
            _event_id, (event_type, *args) = event
            if event_type == "c":
                self._sid = args[0]
            elif event_type == "S":
                self._gsession = args[0]
            else:
                await self._process_event(event_type, args)

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
        Must be linked prior to this.

        :raises NotLinkedException: client is not yet linked, first pair or refresh authorization
        """

        if not self.linked():
            raise NotLinkedException("Not linked")

        body = {"lounge_token": self.auth.lounge_id_token}

        url = f"{api_base}/pairing/get_screen_availability"

        result = await self._required_session.post(url=url, data=body)
        status = await result.json()
        if "screens" in status and len(status["screens"]) > 0:
            return status["screens"][0]["status"] == "online"

        return False

    async def connect(self) -> bool:
        """Attempt to connect using the previously set tokens.

        :raises NotSupportedException: screen does not allow lounge client
        :raises NotLinkedException: client is not yet linked, first pair or refresh authorization
        """
        if not self.linked():
            raise NotLinkedException("Not linked")

        connect_body = {
            "app": "web",
            "mdx-version": "3",
            "name": self.device_name,
            "id": self.auth.screen_id,
            "device": "REMOTE_CONTROL",
            "capabilities": "que,dsdtr,atp,vsp",
            "magnaKey": "cloudPairedDevice",
            "ui": "false",
            "deviceContext": "user_agent=dunno&window_width_points=&window_height_points=&os_name=android&ms=",
            "theme": "cl",
            "loungeIdToken": self.auth.lounge_id_token,
        }
        connect_url = f"{api_base}/bc/bind?RID=1&VER=8&CVER=1&auth_failure_option=send_error"
        async with self._required_session.post(url=connect_url, data=connect_body) as resp:
            try:
                text = await resp.text()
                if resp.status == 401:
                    self._lounge_token_expired()
                    return False

                if resp.status != 200:
                    self._logger.warning("Unknown reply to connect %i %s", resp.status, resp.reason)
                    return False
                lines = text.splitlines()
                async for events in self._parse_event_chunks(as_aiter(lines)):
                    await self._process_events(events)
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

    def _common_connection_parameters(self) -> Dict[str, Any]:
        return {
            "name": self.device_name,
            "loungeIdToken": self.auth.lounge_id_token,
            "SID": self._sid,
            "AID": self._last_event_id,
            "gsessionid": self._gsession,
            "device": "REMOTE_CONTROL",
            "app": "youtube-desktop",
            "VER": "8",
            "v": "2",
        }

    async def subscribe(self) -> None:
        """Start listening for events. Updates will be sent to the event_listener passed when creating this object.

        :raises NotSupportedException: screen does not allow lounge client
        :raises NotConnectedException: the client is not yet connected to the screen
        """
        if not self.connected():
            raise NotConnectedException("Not connected")

        params = {
            **self._common_connection_parameters(),
            "RID": "rpc",
            "CI": "0",
            "TYPE": "xmlhttp",
        }
        url = f"{api_base}/bc/bind"
        self._logger.info("Subscribing to lounge id %s", self.auth.lounge_id_token)
        async with self._required_session.get(
            url=url, params=params, timeout=ClientTimeout()
        ) as resp:
            try:
                if not self._handle_session_result(resp.status, resp.reason or ""):
                    return

                async for events in self._parse_event_chunks(iter_response_lines(resp.content)):
                    await self._process_events(events)
                    if not self.connected():
                        break
                self._logger.info("Subscribe completed, status %i %s", resp.status, resp.reason)
            except ClientPayloadError:
                self._logger.exception(
                    "Handle subscribe payload error, status %s reason %s",
                    resp.status,
                    resp.reason,
                )
            except asyncio.CancelledError:
                raise
            except:
                self._logger.exception(
                    "Handle subscribe failed, status %s reason %s",
                    resp.status,
                    resp.reason,
                )
                raise

    async def disconnect(self) -> bool:
        """Disconnect from the current session.

        :raises NotConnectedException: the client is already not connected
        """
        if not self.connected():
            raise NotConnectedException("Not connected")

        command_body = {
            "ui": "",
            "TYPE": "terminate",
            "clientDisconnectReason": "MDX_SESSION_DISCONNECT_REASON_DISCONNECTED_BY_USER",
        }
        params = {
            **self._common_connection_parameters(),
            "CVER": "1",
            "RID": self._command_offset,
            "auth_failure_option": "send_error",
        }
        url = f"{api_base}/bc/bind"
        async with self._required_session.post(url=url, data=command_body, params=params) as resp:
            try:
                response_text = await resp.text()
                if not self._handle_session_result(resp.status, response_text):
                    return False
                resp.raise_for_status()
                return True
            except:
                self._logger.exception("Disconnect failed")
                raise

    async def _command(self, command: str, command_parameters: Optional[dict] = None) -> bool:
        """Issue given command with parameters.

        :raises NotConnectedException: the client is not connected to the screen
        """
        if not self.connected():
            raise NotConnectedException("Not connected")

        command_body = {"count": 1, "ofs": self._command_offset, "req0__sc": command}
        if command_parameters:
            for cmd_param in command_parameters:
                value = command_parameters[cmd_param]
                command_body[f"req0_{cmd_param}"] = value

        self._command_offset += 1
        params = {
            **self._common_connection_parameters(),
            "RID": self._command_offset,
        }
        url = f"{api_base}/bc/bind"
        async with self._required_session.post(url=url, data=command_body, params=params) as resp:
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

    async def play_video(self, video_id: str) -> bool:
        """Sends setPlaylist command to screen to play a specific video

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("setPlaylist", {"videoId": video_id})

    async def pause(self) -> bool:
        """Sends pause command to screen

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("pause")

    async def previous(self) -> bool:
        """Sends previous command to screen

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("previous")

    async def next(self) -> bool:
        """Sends next command to screen

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("next")

    async def seek_to(self, time: float) -> bool:
        """Seek to given time (seconds)

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("seekTo", {"newTime": time})

    async def skip_ad(self) -> bool:
        """Skips ad if possible

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("skipAd")

    async def set_auto_play_mode(self, enabled: bool) -> bool:
        """Set auto play mode enabled/disabled

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command(
            "setAutoplayMode", {"autoplayMode": "ENABLED" if enabled else "DISABLED"}
        )

    async def set_volume(self, volume: int) -> bool:
        """Sets volume to given value (0-100)

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("setVolume", {"volume": volume})

    async def set_playback_speed(self, speed: float) -> bool:
        """Sets the playback speed to given value (0.25-2)

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("setPlaybackSpeed", {"playbackSpeed": speed})

    async def send_dpad_command(self, button_input: DpadCommand) -> bool:
        """Sends a dpad command like a remote.

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("dpadCommand", {"key": button_input})

    async def set_closed_captions(self, language_code: Optional[str], video_id: str):
        """
        Sets the closed captions to the provided BCP-47 language_code if available.
        Provide the language_code as None to toggle closed captions to off.
        video_id is always required.

        :raises NotConnectedException: the client is not connected to the screen
        """
        lang = language_code if language_code is not None else ""
        return await self._command("setSubtitlesTrack", {"languageCode": lang, "videoId": video_id})

    async def get_now_playing(self) -> bool:
        """Requests a now playing update from the screen.

        :raises NotConnectedException: the client is not connected to the screen
        """
        return await self._command("getNowPlaying")
