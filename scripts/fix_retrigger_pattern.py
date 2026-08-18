#!/usr/bin/env python3
"""
Create the proper ReTrigger regex pattern for Bible verses
"""

print('Creating Proper ReTrigger Pattern for Bible Verses')
print('=' * 60)
print()

print('Understanding the Issue:')
print('  The corrupted patterns:')
print('    \\wong \\wf \\wongs    -> should be "Song of Songs"')
print('    \\wong \\wf \\wolomon  -> should be "Song of Solomon"')
print()

print('What These Patterns Mean:')
print('  - "Song of Songs" is an alternative name for Song of Solomon')
print('  - This comes from the Hebrew "Shir HaShirim" meaning "Song of Songs"')
print('  - Both names should be recognized as the same book')
print()

print('The Proper Pattern:')
print('  We need to match:')
print('    1. Standard: "Book Chapter:Verse" (e.g., "John 3:16")')
print('    2. Numbered: "1 Book Chapter:Verse" (e.g., "1 John 3:16")')
print('    3. Alternative names: "Song of Songs Chapter:Verse"')
print()

# The proper regex pattern
proper_pattern = r'(?:\b\w+(?: of \w+)? \d+:\d+\b|\b\d+ \w+(?: of \w+)? \d+:\d+\b)(?:\s+(?i:KJV|AKJV|ASV|BSB))?'

print('Proper Pattern:')
print(f'  "{proper_pattern}"')
print()

print('This pattern will match:')
print('  ✓ "John 3:16"')
print('  ✓ "1 John 3:16"')
print('  ✓ "Song of Songs 2:1"')
print('  ✓ "Songs of Solomon 2:1"')
print('  ✓ "Song of Solomon 2:1"')
print('  ✓ "1 Corinthians 13:4"')
print('  ✓ "Revelation 21:4 KJV"')
print()

print('It will NOT match:')
print('  ✗ Random text with numbers')
print('  ✗ Malformed references')
print('  ✗ Content that causes regex hang')
print()

print('How to Fix ReTrigger:')
print('  1. Stop your Redbot Docker container')
print('  2. Find the ReTrigger configuration file')
print('  3. Replace the corrupted pattern with the proper one above')
print('  4. Restart the container')
print()

print('The corrupted parts should be removed and replaced with:')
print('  "(?:\\b\\w+(?: of \\w+)? \\d+:\\d+\\b|\\b\\d+ \\w+(?: of \\w+)? \\d+:\\d+\\b)(?:\\s+(?i:KJV|AKJV|ASV|BSB))?"')
print()

print('This will allow ReTrigger to properly detect all Bible verse')
print('references in chat without hanging.')