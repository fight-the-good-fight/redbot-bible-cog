#!/usr/bin/env python3
"""
Fix the settings.json by sanitizing notes that contain bible references
"""

import json
import re

# Load the original settings
with open('scripts/settings.json', 'r') as f:
    settings = json.load(f)

notes = settings['718395193090375700']['GLOBAL']['Notes']

print('Fixing Settings.json')
print('=' * 50)
print()

# Pattern to find bible references in note text
bible_ref_pattern = r'\b\w+ \d+:\d+\b'

fixed_notes = []
issues_found = 0

for note in notes:
    note_text = note['note']
    
    # Check if note text contains bible references
    matches = re.findall(bible_ref_pattern, note_text)
    
    if matches:
        issues_found += 1
        print(f'Fixing note {note[\"number\"]}: {note[\"book\"]} {note[\"chapter\"]}:{note[\"verse\"]}')
        print(f'  References found in text: {matches}')
        
        # Replace bible references with [reference] to avoid regex issues
        sanitized_text = re.sub(bible_ref_pattern, r'[\\g<0>]', note_text)
        
        # Create a new note with sanitized text
        fixed_note = {
            "number": note['number'],
            "book": note['book'],
            "chapter": note['chapter'],
            "verse": note['verse'],
            "note": sanitized_text
        }
        fixed_notes.append(fixed_note)
        
        print(f'  Sanitized text: {sanitized_text[:60]}...')
        print()
    else:
        # Keep the note as-is
        fixed_notes.append(note)

# Create the fixed settings structure
fixed_settings = {
    "718395193090375700": {
        "GLOBAL": {
            "Notes": fixed_notes
        }
    }
}

# Write to file
with open('scripts/settings_fixed.json', 'w') as f:
    json.dump(fixed_settings, f, indent=2)

print('Fixing Complete!')
print('=' * 50)
print()
print(f'Total notes: {len(fixed_notes)}')
print(f'Issues fixed: {issues_found}')
print()
print('The fixed settings.json file is ready at: scripts/settings_fixed.json')
print()
print('This file sanitizes notes that contain bible references in their text')
print('to prevent the ReTrigger regex from hanging.')