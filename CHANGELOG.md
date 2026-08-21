# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.2.1 (2026-08-21)

### Features

- Lookup memories and changes render as a blockquote, set apart from the verse
  text; a blank line separates the meta from the next verse.

## v1.2.0 (2026-08-21)

### Features

- Lookup supports whole chapters, single verses, ranges, and verse lists.
- ReTrigger pattern is now a short generic regex (no book-name list).

### Bug Fixes

- Whole-chapter lookups no longer drop the last verse.
- Whole-chapter lookups no longer crash for ASV/BSB.
- Unknown books no longer trigger an error reply.

## v1.1.1 (2026-08-20)

### Bug Fixes

- Fixed a crash when paginating lookup results.

## v1.1.0 (2026-08-20)

### Features

- KJV "changes" lookup for verses.
- Memories stored in a dedicated file, with migration tooling.

### Bug Fixes

- More reliable command responses.

## v1.0.1 (2026-06-29)

### Features

- Faster Bible search backed by a local SQLite index.

### Bug Fixes

- More reliable lookups, searches, and notes.

### Documentation

- Clarified Redbot installation from the git repository.

### Chores

- Added release automation and CI checks.

## v1.0.0 (2023-09-24)

Initial release.
