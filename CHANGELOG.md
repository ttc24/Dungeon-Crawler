# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Enemies now select weighted combat intents (Aggressive, Defensive or Unpredictable) and telegraph their actions to the player.
- Console script entry point `dungeoncrawler`.
- Defined project metadata (name, version, required Python) in `pyproject.toml`.
- Entering floor 10 now increases enemy health and damage scaling unless debug mode is enabled.
- Elite enemies resist negative status effects for longer, halving durations applied to them.
- Floor 12 "Hunted" hooks introducing Blood Torrent and Compression Sickness along with counter consumables.
- Floor 13 "Anti-Magic" hooks adding Mana Lock, Hex of Dull Wards and the Suppression Ring item.
- Floor 14 "Entropy" hooks introducing Entropic Debt, Spiteful Reflection and the Entropy Vent Stone item.
- Floor 15 "Pestilence" hooks introducing Brood Bloom infections, Miasma Carrier aura, Broodling enemies and mitigation consumables.
- Floor 16 "Time Weirdness" hooks introducing Temporal Lag, Haste Dysphoria and the Anchor consumable.
- Floor 17 "Oaths & Curses" hooks introducing Fester Mark and Soul Tax with altar donations to cleanse.
- Floor 18 "Broadcast Finale" hooks introducing Spotlight and Audience Fatigue mechanics with Signal Jammer, Smoke Bomb and Rewrite consumables.
- Floor 17 now features two sequential mini-boss encounters with restorative boons between them before the Gloom Shade.
- Floor 18's finale is a five-phase confrontation where players may exit early after any phase for a scaling score bonus.

## [0.9.0b1] - 2025-08-11
### Added
- Pre-release package for beta testing.
- Issue templates for bug reports and suggestions.

### Fixed
- Addressed packaging configuration to enable pre-release builds.
