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
