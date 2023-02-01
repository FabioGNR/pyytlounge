# YouTube Lounge API wrapper written in Python (WIP)

## Setup

Activate virtual environment:

- create `python -m venv .venv`
- activate `source .venv/bin/activate`

## How to use

1. Now you need a screen_id and loungeToken. For now the easiest way is through manual pairing.
   - Try `python manual_pairing.py` and enter the pairing code from the YouTube app settings.
2. Copy variables_example.py to variables.py and enter screen id and lounge token there.
3. `python main.py`

## Thanks

- https://github.com/henriquekano/youtube-lounge-api

### Publish to pypi

1. Update pyproject.toml
2. `python -m build`
3. `python -m twine upload dist/*`
