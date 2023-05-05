# YouTube Lounge API wrapper written in Python (WIP)

## Setup

Activate virtual environment:

- create `python -m venv .venv`
- activate `source .venv/bin/activate`

## How to use

`python test.py` will run an interactive demo.

## Release Notes

See [CHANGELOG](CHANGELOG.md).

## Thanks

- https://github.com/henriquekano/youtube-lounge-api

### Publish to pypi

1. Update pyproject.toml
2. `python -m build`
3. `python -m twine upload dist/*`
