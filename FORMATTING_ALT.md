  Pattern: define sections as ordered list of functions, each returns a field dict or None (skipped if condition fails),
  then assemble.

  import discord

  def section_summary(data):
      return {"name": "Summary", "value": data["summary"], "inline": False}

  def section_links(data):
      if not data.get("links"):
          return None
      body = "\n".join(f"[{l['label']}]({l['url']})" for l in data["links"])
      return {"name": "Links", "value": body, "inline": False}

  def section_items(data):
      items = data.get("items")
      if not items:
          return None
      body = "\n".join(f"• {i}" for i in items)
      return {"name": f"Items ({len(items)})", "value": body[:1024], "inline": False}

  def section_status(data):
      if not data.get("flagged"):
          return None
      return {"name": "⚠️ Flagged", "value": data["flag_reason"], "inline": True}

  SECTIONS = [section_summary, section_links, section_items, section_status]

  def build_embed(data, title, color=discord.Color.blurple()):
      embed = discord.Embed(title=title, color=color)
      for fn in SECTIONS:
          field = fn(data)
          if field:
              embed.add_field(**field)
      return embed

  Why this fits your asks:
  - Conditional output — each section fn returns None to skip, no template {% if %} needed
  - Variable-length lists — build the joined string inline, no loop syntax to fight
  - Links — Discord markdown [label](url) works directly in field values
  - Reordering sections — just reorder the SECTIONS list, nothing else touches structure
  - 1024-char field cap — truncate/paginate inside each section fn as needed

  Keep SECTIONS list per-embed-type (e.g. RANK_SECTIONS, ALERT_SECTIONS) in a templates.py/embeds.py module per cog.
  Data dict stays plain — easy to unit test section fns in isolation without touching discord.py at all.

