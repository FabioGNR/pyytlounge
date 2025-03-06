from typing import TypedDict


class _PlaybackStateData(TypedDict):
    """Representation of playback state as reported by API"""

    currentTime: str
    duration: str
    state: str


class _NowPlayingData(_PlaybackStateData):
    """Representation of now playing state as reported by API"""

    videoId: str


class _VolumeChangedData(TypedDict):
    volume: str
    muted: str


class _AutoplayModeChangedData(TypedDict):
    autoplayMode: str


class _DeviceInfo(TypedDict):
    brand: str
    model: str
    os: str


class _Device(TypedDict):
    name: str
    type: str
    id: str
    deviceInfo: str  # json string


class _LoungeStatus(TypedDict):
    devices: str  # json string containing list of __Device
