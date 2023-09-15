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
