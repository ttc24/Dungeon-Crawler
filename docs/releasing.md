# Releasing

Follow these steps to publish a new version of *Dungeon Crawler* to PyPI.

1. Ensure the version number in `pyproject.toml` is updated.
2. Install required build tools:
   ```bash
   python -m pip install --upgrade build twine
   ```
3. Build the distribution archives:
   ```bash
   python -m build
   ```
4. Upload the artifacts to PyPI:
   ```bash
   twine upload dist/*
   ```
5. Tag the release in git and push the tag:
   ```bash
   git tag vX.Y.Z
   git push --tags
   ```
