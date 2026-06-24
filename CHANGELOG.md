# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Faster Bible search backed by a local SQLite index for the bundled verse data.
- `bible isearch` for case-insensitive verse searching.
- Spellchecking in CI.
- Release automation for tag/changelog generation.

### Changed
- Broke the cog into smaller modules for lookup, search, memory, and translations.
- Reworked the Bible lookup and search command implementations for clearer control flow.
- Updated the README to explain that Redbot installs from the git repository, not GitHub release assets.

### Fixed
- Corrected translation detection and search helper behavior.
- Cleaned up note handling and lookup edge cases.
- Restored exported helpers expected by the existing tests.

### Docs
- Added Redbot install guidance and release notes to the repository docs.

### Release process
- Release tags are now generated from `main` with `release-please`.
- The release PR and changelog describe the repo-first Redbot install flow.

## v1.0.0

2026-06-19

Initial release.
