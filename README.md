# Red-DiscordBot Bible Cog

Look up Bible verses, search scripture text, and attach personal notes to verses or chapters.

## Why use this cog?

- Search the Bible without external API calls.
- Read verses, chapters, or verse ranges directly in Discord.
- Keep personal notes on verses and chapters inside Redbot.

This cog includes three bundled Bible translations:

- AKJV — American King James Version
- ASV — American Standard Version
- BSB — Berean Study Bible

All verse data is bundled locally. No external Bible API is used.

## Installation

Redbot installs cogs from the git repository, not from GitHub release assets.

1. Add this repository as a repo cog:

       .repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog
2. Install and load:

       .cog install anvil bible
       .load bible

Release tags and release notes are still published for changelog/history tracking.

## Commands

| Command | What it does |
| --- | --- |
| `bible version` | Show the Bible cog version. |
| `bible translations` | List the bundled Bible translations. |
| `bible lookup <verse>` | Show a verse, chapter, or verse range. |
| `bible search <text>` | Search for matching text across the Bible. |
| `bible isearch <text>` | Search for matching text without case sensitivity. |
| `memory add <verse> <note>` | Save a note for a verse or chapter. |
| `memory remove <id>` | Delete a saved note by its ID. |
| `memory list` | List saved notes, optionally filtered by book or chapter. |
| `removeallnotes` | Clear all stored notes (owner only). |

### Examples

- `bible lookup john 3:16`
- `bible lookup psalms 23`
- `bible lookup john 3:16-18`
- `bible search beloved`
- `bible isearch beloved`
- `memory add john 3:16 "God loved us first"`
- `memory list john 3`

## Notes Storage

User notes are stored in Redbot's `Config` system, keyed by the verse or chapter
identifier. Notes persist across server restarts but are scoped to the guild where they
were added.
