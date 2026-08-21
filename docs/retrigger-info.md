# ReTrigger Bible Verse Pattern

## Current Regex Pattern

### Pattern
```python
(?i)(?:\b\d+ \w+(?: of \w+)? \d+:(?:\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)?|\b\w+(?: of \w+)? \d+:(?:\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)?)(?:\s+(?i:KJV|AKJV|ASV|BSB))?
```

### Compilation
```python
re.compile(pattern)  # the inline (?i) makes it case-insensitive regardless of compile flags
```

Print it any time with:
```
.venv/bin/python scripts/fix_retrigger_pattern.py
```

## Supported Syntaxes

The colon after the chapter number is **required**. The verse part is optional.

| Reference | Meaning |
|---|---|
| `Genesis 1:` | whole chapter |
| `Genesis 1:1` | verse 1 |
| `Genesis 1:1-3` | verses 1 through 3 |
| `Genesis 1:1,5` | verses 1 and 5 (in the order typed) |
| `Genesis 1:1-3,7` | mixed range and single verses |
| `1 John 1:1` | numbered books |
| `Song of Songs 2:1` | multi-word book names |
| `Revelation 21:4 KJV` | optional translation code |

## How It Works

The pattern is intentionally **generic** — it has no book-name list. The colon is a
strong signal that a verse reference is present, so a plain `\w+` book name is enough
to match. The cog enforces "real book" at lookup time:

- **Unknown book → silence.** If the matched book has no bundled data (a typo like
  `Genesiss 1:1`, or an apocryphal book not yet bundled like `Tobit 1:1`), the cog
  replies with nothing. This is what makes the generic pattern safe: a false positive
  like `step 2:` or `the ratio is 5:3` matches the regex but produces no reply.
- **Out-of-range → error.** If the book is real but the chapter or verse is out of
  range (`Genesis 99:1`, `Genesis 1:999`), the cog replies `Invalid chapter or verse`.

### Apocrypha

Because there is no book list, adding apocryphal data to the cog makes those
references work with **no regex change**. `Tobit 1:1` is silent today (no data) and
works automatically once the data is bundled.

## What This Pattern Matches

### ✅ Standard References
- `"John 3:16"`, `"john 3:16"`, `"JOHN 3:16"` (case-insensitive)

### ✅ Numbered Books
- `"1 Corinthians 13:4"`, `"2 Samuel 12:23"`

### ✅ Multi-Word Book Names
- `"Song of Songs 2:1"`, `"Song of Solomon 2:1"`

### ✅ Whole Chapters
- `"Genesis 1:"`, `"1 John 1:"`

### ✅ Verse Ranges and Lists
- `"Genesis 1:1-3"`, `"Genesis 1:1,5"`, `"Genesis 1:1-3,7"`

### ✅ With Translation Codes
- `"John 3:16 KJV"`, `"Song of Songs 2:1 ASV"`

### ✅ In Real Chat Messages
- `"I read Genesis 1:1 today"`
- `"The famous verse is 1 Corinthians 13:4"`

### ✅ Distinct Matches
- `"1 John 1:1"` matches as `"1 John 1:1"` (with the number prefix)
- `"John 1:1"` matches as `"John 1:1"` (without it)
- Both are correctly identified as different references

## Pattern Breakdown

```
(?i)                          - inline case-insensitive flag
(?:                           - non-capturing group: two alternatives
  \b\d+ \w+(?: of \w+)?       -   numbered book: "1 " + name (+ " of " + word)
  | \b\w+(?: of \w+)?         -   plain book: name (+ " of " + word)
  \d+:                        -   space + chapter number + required colon
  (?:\d+(?:-\d+)?             -   optional verse: a number
     (?:,\d+(?:-\d+)?)*)?    -     (+ optional range end, + comma-separated items)
)
(?:\s+(?i:KJV|AKJV|ASV|BSB))? - optional: space + translation code
```

## Corrupted Pattern (DO NOT USE)
```python
# OLD CORRUPTED PATTERN (DO NOT USE)
(?:\w+ \d+:\d+[\w-]\d+|\wong \wf \wongs \d+:\d+[\w-]\d+|\wong \wf \wolomon \d+:\d+[\w-]\d+|\d+ \w+ \d+:\d+[\w-]\d+|\d\D+ \d+:\d+[\w-]\d+|\w+ \d+:\d+|\wong \wf \wongs \d+:\d+|\wong \wf \wolomon \d+:\d+|\d+ \w+ \d+:\d+|\d\D+ \d+:\d+)(?:\s+(?i:KJV|AKJV|ASV|BSB))?
```

**Problems:**
- Contains suspicious typos: `\wong`, `\wf`, `\wongs`, `\wolomon`
- Corrupted attempts to match "Song of Songs"
- Overly complex with redundant alternatives
- Potential catastrophic backtracking / regex timeouts

## Testing

The cog's lookup behavior — the four syntaxes, silence on unknown books, and the
out-of-range error — is covered by unit tests in `bible/tests/lookup_command_test.py`.

Run them with:
```
.venv/bin/python -m pytest bible/tests/
```