import aiohttp

CHANGES_API_URL = "https://search.thesupernaturalbiblechanges.com/v1/GetChangesByChapter"
CHANGES_DETAIL_URL = "https://search.thesupernaturalbiblechanges.com/changes/{change_id}"
REQUEST_TIMEOUT_SECONDS = 5


async def get_changes_for_chapter(book_number: int, chapter: int) -> list[dict]:
    """Query the supernatural bible changes API for one chapter.

    Returns a list of change dicts, or an empty list on any error.
    """
    payload = {"bookNumber": book_number, "chapterNumber": chapter}
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(CHANGES_API_URL, json=payload) as response:
                if response.status != 200:
                    return []
                data = await response.json(content_type=None)
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def format_change_lines(change: dict) -> list[str]:
    """Build Discord description lines describing one recorded change."""
    bcv = change.get("BCV") or ""
    lines = [f"**Change recorded for {bcv} (KJV):**"]
    notes = str(change.get("notes") or "").strip()
    if notes:
        lines.append("Notes:")
        lines.extend(
            f"- {line.strip()}" for line in notes.splitlines() if line.strip()
        )
    summary = change.get("memorySummary") or {}
    restored_text = summary.get("restoredText")
    if restored_text:
        lines.append("**Possible Restoration:**")
        lines.append(str(restored_text))
    changed_from = summary.get("changedFrom")
    changed_to = summary.get("changedTo")
    if changed_from or changed_to:
        lines.append(f"- changed: {changed_from or '?'} to {changed_to or '?'}")
    change_id = change.get("ID")
    if change_id:
        lines.append(CHANGES_DETAIL_URL.format(change_id=change_id))
    return lines