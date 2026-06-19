# redbot-bible-cog

## Installing this cog:

Remove existing cog if needed:

```DISCORD
.cog uninstall bible
```

Add the repo, install, and load

```DISCORD
.repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog
.cog install anvil bible
.load bible
```

Updating the repo (load from scratch)

```DISCORD
.cog uninstall bible
.repo update
.cog install anvil bible
.load bible
```

Update cog when it is already installed/running

```DISCORD
.unload bible
.cog update
.restart
.load bible
```

## Adding a memory/note

```DISCORD
.memory add genesis 1:1 another memory
```

```DISCORD
.memory list
```

Get memories for specific verse
```DISCORD
.memory list genesis 1:1
```

## Notes

Notes are stored in memory like this:

```JSON
{"718395193090375700": {"GLOBAL": {"Notes": [{"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "Heavens was changed to heaven."}]}}}
```

```JSON
{"718395193090375700": {"GLOBAL": {"Notes": [{"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "Heavens was changed to heaven."}, {"number": 2, "book": "Genesis", "chapter": 1, "verse": 1, "note": "another memory"}]}}}
```

## triggering

```DISCORD
.retrigger command bible-parser "\w+ \d+:\d+[\w-]\d+|\wong \wf \wongs \d+:\d+[\w-]\d+|\wong \wf \wolomon \d+:\d+[\w-]\d+|\d+ \w+ \d+:\d+[\w-]\d+|\d\D+ \d+:\d+[\w-]\d+|\w+ \d+:\d+|\wong \wf \wongs \d+:\d+|\wong \wf \wolomon \d+:\d+|\d+ \w+ \d+:\d+|\d\D+ \d+:\d+" bible lookup {0}
```
