#!/usr/bin/env python3
"""
Commentaries Migration Script v2

This script extracts commentaries from your backup file and converts them
to Red-DiscordBot Bible cog notes format.

The backup file contains a "commentaries" section where each book has a list
of commentary entries, each with chapter, verse, and text information.
"""

import json


def analyze_commentaries(backup_path):
    """Analyze the commentaries section of the backup file"""
    try:
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        commentaries = backup_data.get('commentaries', {})
        
        print("Commentaries Analysis")
        print("=" * 50)
        print(f"Total books with commentaries: {len(commentaries)}")
        print()
        
        # Count total commentaries with text
        total_commentaries = 0
        for book, entries in commentaries.items():
            for entry in entries:
                text = entry.get('text', '')
                if text and text.strip():
                    total_commentaries += 1
        
        print(f"Total commentaries (with text): {total_commentaries}")
        print()
        
        # Show sample commentaries
        print("Sample Commentaries:")
        sample_count = 0
        for book, entries in commentaries.items():
            for entry in entries:
                text = entry.get('text', '')
                if text and text.strip():
                    chapter = entry.get('chapter', '?')
                    verse = entry.get('verse', '?')
                    print(f"  {book} {chapter}:{verse}")
                    print(f"    Text: {text[:60]}..." if len(text) > 60 else f"    Text: {text}")
                    sample_count += 1
                    if sample_count >= 5:
                        break
            if sample_count >= 5:
                break
        
        return backup_data
        
    except Exception as e:
        print(f"Error analyzing commentaries: {e}")
        return None


def create_red_discordbot_settings_from_commentaries(commentaries_data, output_path="settings.json"):
    """Create Red-DiscordBot settings.json from commentaries"""
    
    commentaries = commentaries_data.get('commentaries', {})
    
    # Convert commentaries to notes
    notes = []
    note_number = 1
    
    for book, entries in commentaries.items():
        for entry in entries:
            text = entry.get('text', '')
            
            # Skip if text is empty or None
            if not text or not text.strip():
                continue
            
            # Create note from commentary
            note = {
                "number": note_number,
                "book": book,
                "chapter": int(entry.get('chapter', 1)),
                "verse": int(entry.get('verse', 1)),
                "note": f"Commentary: {text}"
            }
            notes.append(note)
            note_number += 1
    
    # Create Red-DiscordBot settings structure
    settings = {
        "718395193090375700": {
            "GLOBAL": {
                "Notes": notes
            }
        }
    }
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print(f"\n✅ Created Red-DiscordBot settings file: {output_path}")
    print(f"   Migrated {len(notes)} notes from commentaries")
    
    return settings


def main():
    """Main migration process"""
    
    backup_path = "./backup.json"
    
    print("Bible Commentaries Migration")
    print("=" * 50)
    print()
    
    # Step 1: Analyze commentaries
    backup_data = analyze_commentaries(backup_path)
    
    if not backup_data:
        return
    
    # Step 2: Check if we have commentaries to migrate
    commentaries = backup_data.get('commentaries', {})
    
    if not commentaries:
        print("\n⚠️  No commentaries found to migrate")
        print("   The backup file does not contain any commentaries.")
        return
    
    # Step 3: Create Red-DiscordBot settings
    print("\n" + "=" * 50)
    print("Creating Red-DiscordBot Settings File")
    print("=" * 50)
    
    settings = create_red_discordbot_settings_from_commentaries(backup_data)
    
    if settings:
        print("\nMigration Summary:")
        print(f"  Source backup: {backup_path}")
        print(f"  Target settings: settings.json")
        print(f"  Notes created: {len(settings['718395193090375700']['GLOBAL']['Notes'])}")
        
        print("\nNext Steps:")
        print("  1. Place settings.json in the bot's data directory:")
        print("     data/red/cogs/Bible/settings.json")
        print("  2. Restart the bot")
        print("  3. Verify notes with: 'memory list'")
        print("  4. You can add more notes manually as needed")
        
        print("\nImportant Notes:")
        print("  - Only commentaries with non-empty text were migrated")
        print("  - Each commentary becomes a note attached to its verse")
        print("  - The note text is prefixed with 'Commentary: ' for clarity")
        print("  - You can edit or remove notes after migration if needed")


if __name__ == "__main__":
    main()