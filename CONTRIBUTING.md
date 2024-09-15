# Contributing

## Releasing

1. Bump version in pyproject.toml and update CHANGELOG.md
2. Place an annotated tag on that commit
3. Push the tag and create the GitHub release

## Docs

View the docs locally:

1. `cd docs`
2. `$(make html && cd _build/html && python -m http.server)`
3. Open `http://localhost:8000`
