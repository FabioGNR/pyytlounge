# 3.2.0

### Breaking changes

- `EventListener.disconnected(self)` signature changed to facilitate event data, should be changed to `disconnected(self, event: DisconnectedEvent)`

### Added

- Detect unsupported 'YouTube TV Kids' client and raise `NotSupportedException` (@dmunozv04)
- `disconnected` event now provides reason if available (@dmunozv04)
- Automatically request playback state when playback speed is changed (@dmunozv04)

### Changed

- Remove `setPlaylist` command when connecting to screen (@dmunozv04)
- Fixed is_available raising incorrect exception

# 3.1.0

### Added

- `ad_state_changed` event (onAdStateChange) (@dmunozv04)
- `ad_playing_changed` event (adPlaying) (@dmunozv04)
- `subtitles_track_changed` event (onSubtitlesTrackChanged) (@dmunozv04)
- `autoplay_up_next_changed` event (autoplayUpNext) (@dmunozv04)
- `playback_speed_changed` event (onPlaybackSpeedChanged) (@dmunozv04)

### Changed

- Fixed volume level not converted to int
- Fixed `NowPlayingEvent.get_thumbnail_url`

# 3.0.1

### Changed

- Fixed issue when connecting to screen without any video playing

# 3.0.0

### Breaking changes

- Listening for events is now done through an EventListener class instead of a single callback. This allows to add events in a flexible way.
  See [migration documentation](https://pyytlounge.readthedocs.io/en/v3.0.0/updating.html#migrate-to-event-listener-v3-x-x).
  If you are using `YtLoungeApi.subscribe` you must update your usage.

### Added

- `volume_changed` event (onVolumeChanged)
- `autoplay_changed` event (onAutoplayModeChanged)
- `send_dpad_command` command to send remote button presses (@sternma)
- `set_playback_speed` command to set video playback speed (@sternma)
- `set_closed_captions` command to set closed captions based on language code or turn it off (@sternma)
- `get_available_captions` helper to retrieve available closed captions for a video using YouTube v3 API (@sternma)

# 2.3.0

### Added

- Add `vsp` capability which allows receiving `playbackSpeed` events @dmunozv04
- `set_auto_play_mode` command: toggle auto play @bertybuttface

# 2.2.1

### Changed

- Fixed compatibility with Python 3.9

# 2.2.0

### Added

- play_video command: play given video using its id @bertybuttface

### Changed

- Fixed exception when using `screen_device_name` before data was received

# 2.1.2

### Changed

- aiohttp dependency is now specified as >=3.11.12

# 2.1.1

### Changed

- Fixed commands not working after refactor

# 2.1.0

### Added

- `pyytlounge.dial.get_screen_id_from_dial()` when given a DIAl endpoint, can retrieve a YouTube screen's ID for pairing.
  With thanks to @dmunozv04 for his implementation in [iSponsorBlockTV](https://github.com/dmunozv04/iSponsorBlockTV) which served as inspiration

### Changed

- Internal refactor, shouldn't be noticable unless internal classes were being used
- `YtLoungeApi.subscribe()` no longer logs `asyncio.CancelledError()`

# 2.0.0

### Added

- Documentation now available at https://readthedocs.org/projects/pyytlounge/

### Changed

- Aiohttp session is now reused to cache DNS responses
- On loungeScreenDisconnected event the lounge token is invalidated.
- BREAKING: the API must now be closed after use to properly clean up aiohttp sessions. Either use the `with` statement or manually call `.close()`.
- BREAKING: the API will now raise unexpected exceptions instead of capturing them.

# 1.7.0

### Changed

- Specify `'ui': 'false'` when connecting to device @dmunozv04.
  This should prevent an [issue with YouTube Kids](https://github.com/FabioGNR/pyytlounge/pull/6)

# 1.6.3

### Changed

- Fixed exception logging
- Add handling for missing expired lounge token

# 1.6.2

### Changed

- aiohttp dependency is now specified as >=3.8.4

# 1.6.1

### Changed

- functions now raise specific exception types for:
  - not paired: NotPairedException
  - not linked: NotLinkedException
  - not connected: NotConnectedException
- logging of exceptions was extended with status code and reason returned by Yt Lounge API

# 1.6.0

### Added

- skip_ad command: tries to skip any current ad @dmunozv04
- set_volume command: change volume @dmunozv04
- disconnect command: disconnect gracefully @dmunozv04

### Changed

- requests dependency removed in favor of aiohttp @dmunozv04
- bump aiohttp version to 3.8.4 @dmunozv04

# 1.5.0

### Added

- Add pytest structure
- Add test for loungeStatus event

### Changed

- Internal fields now use single underscore instead of double
