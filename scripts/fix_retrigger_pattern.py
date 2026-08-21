#!/usr/bin/env python3
"""
Print the ReTrigger regex pattern for Bible verse references.

The pattern is intentionally generic (no book-name list). The colon after the
chapter number is the signal that a reference is present; the cog enforces
"real book" at lookup time and stays silent for books it has no data for.
"""

PATTERN = (
    r"(?i)(?:\b\d+ \w+(?: of \w+)? "
    r"\d+:(?:\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)?"
    r"|\b\w+(?: of \w+)? "
    r"\d+:(?:\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)?)"
    r"(?:\s+(?i:KJV|AKJV|ASV|BSB))?"
)

print("ReTrigger pattern for Bible verse references")
print("=" * 60)
print()
print("Pattern:")
print(f'  "{PATTERN}"')
print()
print("Syntaxes supported (the colon is required):")
print('  "Genesis 1:"        -> whole chapter')
print('  "Genesis 1:1"       -> verse 1')
print('  "Genesis 1:1-3"     -> verses 1 through 3')
print('  "Genesis 1:1,5"     -> verses 1 and 5 (in the order typed)')
print('  "Genesis 1:1-3,7"   -> mixed range and single verses')
print('  "1 John 1:1"        -> numbered books')
print('  "Song of Songs 2:1" -> multi-word book names')
print('  "Revelation 21:4 KJV" -> optional translation code')
print()
print("Why no book-name list:")
print("  The colon is a strong signal, so a generic \\w+ book name is enough.")
print("  The cog stays SILENT for books it has no data for (a typo, or an")
print("  apocryphal book not yet bundled), so a false positive like")
print('  "step 2:" or "the ratio is 5:3" produces no reply. Adding apocryphal')
print("  data later makes those references work with no regex change.")
print()
print("Out-of-range references (a real book, but a bad chapter or verse)")
print("reply with:")
print('  "Invalid chapter or verse"')
print()
print("How to apply in ReTrigger:")
print("  1. Stop your Redbot Docker container")
print("  2. Find the ReTrigger configuration file")
print("  3. Replace the pattern with the one above")
print("  4. Restart the container")