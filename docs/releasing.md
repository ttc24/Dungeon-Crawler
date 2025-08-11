# Releasing

Steps to publish a new version of Dungeon Crawler to PyPI.

1. Ensure `pyproject.toml` has the correct version.
2. Commit and tag the release:
   ```bash
   git commit -am "Release vX.Y.Z"
   git tag vX.Y.Z
   ```
3. Build and upload the package:
   ```bash
   python -m pip install build twine
   python -m build
   twine upload dist/*
   ```
4. Push commits and tags:
   ```bash
   git push && git push --tags
   ```
