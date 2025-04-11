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


class _AdStateData(TypedDict):
    adState: str
    currentTime: str
    isSkipEnabled: str


class _AdPlayingData(_AdStateData):
    adVideoId: str
    adVideoUri: str
    adTitle: str
    isBumper: str
    isSkippable: str
    clickThroughUrl: str
    adSystem: str
    adNextParams: str
    remoteSlotsData: str
    contentVideoId: str
    duration: str


class _SubtitlesTrackData(TypedDict):
    videoId: str
    trackName: str
    languageCode: str
    sourceLanguageCode: str
    languageName: str
    kind: str
    vss_id: str
    captionId: str
    style: str


class _AutoplayUpNextData(TypedDict):
    videoId: str


class _PlaybackSpeedData(TypedDict):
    playbackSpeed: str


class _DisconnectedData(TypedDict):
    reason: str