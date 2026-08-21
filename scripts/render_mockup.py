#!/usr/bin/env python3
"""Render a Discord mockup HTML file to a tight-cropped PNG.

Opens the mockup in headless Chrome, measures the content box, sizes the
viewport to exactly that box, and screenshots a PNG with no grey margin.
This is the render half of the preview loop: keep the mockup HTML in sync
with the embed (see preview_lookup.py), then render it to an image.

    python scripts/render_mockup.py /tmp/discord_mockup.html
    python scripts/render_mockup.py /tmp/discord_mockup.html -o out.png
    python scripts/render_mockup.py /tmp/discord_mockup.html --scale 2

By default the output is <html>.png next to the input. --scale 2 produces a
sharper 2x image (e.g. 1656x642 instead of 828x321) for closer inspection.

Dev-only dependency (not a cog runtime dep -- do not add to
bible/requirements.txt):

    .venv/bin/python -m pip install playwright

Uses the system Google Chrome by default (no browser download). If Chrome is
not installed, run `playwright install chromium` and pass --browser chromium.
"""
import argparse
import sys
from pathlib import Path

# JS that measures the content box: the element's bounding rect plus the
# body padding around it, so the crop keeps the same margin as the page.
_MEASURE_JS = """(sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(document.body);
    return {
        width: Math.ceil(r.right + parseFloat(cs.paddingRight)),
        height: Math.ceil(r.bottom + parseFloat(cs.paddingBottom)),
    };
}"""


def _launch(p, browser: str):
    """Launch a headless browser. `chrome` uses the system Google Chrome."""
    if browser == "chrome":
        try:
            return p.chromium.launch(channel="chrome", headless=True)
        except Exception as exc:  # noqa: BLE001 - surface a friendly hint
            raise SystemExit(
                "error: could not launch system Google Chrome "
                f"({exc.__class__.__name__}). Install Chrome, or run "
                "`playwright install chromium` and pass --browser chromium."
            ) from exc
    return p.chromium.launch(headless=True)


def render(html_path: Path, out_path: Path, selector: str, scale: float, browser: str) -> dict:
    """Render html_path to a tight-cropped PNG at out_path. Returns the box."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            f"error: playwright is not installed. Run: {sys.executable} -m pip install playwright"
        ) from exc

    with sync_playwright() as p:
        browser_inst = _launch(p, browser)
        try:
            page = browser_inst.new_page(device_scale_factor=scale)
            page.goto(html_path.as_uri())
            page.wait_for_load_state("load")

            box = page.evaluate(_MEASURE_JS, selector)
            if box is None:
                raise SystemExit(
                    f"error: selector {selector!r} not found in {html_path}"
                )

            # Size the viewport to the content so the capture is a tight crop.
            page.set_viewport_size({"width": box["width"], "height": box["height"]})
            page.screenshot(path=str(out_path), type="png")
        finally:
            browser_inst.close()
    return box


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a Discord mockup HTML to a tight-cropped PNG."
    )
    parser.add_argument("html", help="Path to the mockup HTML file")
    parser.add_argument(
        "-o", "--output", help="Output PNG path (default: <html>.png)"
    )
    parser.add_argument(
        "--selector",
        default=".message",
        help="CSS selector for the content box to crop to (default: .message)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Device scale factor for sharper output (default: 1.0)",
    )
    parser.add_argument(
        "--browser",
        default="chrome",
        choices=["chrome", "chromium"],
        help="Browser to use (default: chrome = system Google Chrome)",
    )
    args = parser.parse_args()

    html_path = Path(args.html).expanduser().resolve()
    if not html_path.is_file():
        raise SystemExit(f"error: HTML file not found: {html_path}")
    out_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else html_path.with_suffix(".png")
    )

    box = render(html_path, out_path, args.selector, args.scale, args.browser)
    print(
        f"rendered {html_path} -> {out_path} "
        f"({box['width']}x{box['height']} @ {args.scale:g}x)"
    )


if __name__ == "__main__":
    main()