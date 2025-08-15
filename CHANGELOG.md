# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Enemies now select weighted combat intents (Aggressive, Defensive or Unpredictable) and telegraph their actions to the player.
- Console script entry point `dungeoncrawler`.
- Defined project metadata (name, version, required Python) in `pyproject.toml`.
- Entering floor 10 now increases enemy health and damage scaling unless debug mode is enabled.
- Elite enemies resist negative status effects for longer, halving durations applied to them.

## [0.9.0b1] - 2025-08-11
### Added
- Pre-release package for beta testing.
- Issue templates for bug reports and suggestions.

### Fixed
- Addressed packaging configuration to enable pre-release builds.
