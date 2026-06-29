from typing import Any, cast

import asyncio

from redbot.core import commands

from bible import translations_command as translations_module


def test_translations_command_builds_embeds_and_menu(monkeypatch):
    pages = ["first page", "second page"]
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        translations_module, "translation_names", {"akjv": "AKJV", "bsb": "BSB"}
    )
    monkeypatch.setattr(translations_module, "pagify", lambda *args, **kwargs: pages)

    async def fake_menu(ctx, embeds, controls, timeout):
        captured["ctx"] = ctx
        captured["embeds"] = embeds
        captured["controls"] = controls
        captured["timeout"] = timeout

    monkeypatch.setattr(translations_module, "menu", fake_menu)

    ctx = cast(commands.Context, object())

    asyncio.run(translations_module.translations(ctx))

    assert captured["ctx"] is ctx
    assert captured["controls"] is translations_module.DEFAULT_CONTROLS
    assert captured["timeout"] == 30
    assert len(captured["embeds"]) == 2
    assert captured["embeds"][0].title == "Available Translations"
    assert captured["embeds"][0].description == "first page"
    assert captured["embeds"][1].description == "second page"


def test_translations_command_formats_translation_list(monkeypatch):
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        translations_module, "translation_names", {"akjv": "AKJV", "bsb": "BSB"}
    )

    def fake_pagify(description, page_length, delims):
        captured["description"] = description
        captured["page_length"] = page_length
        captured["delims"] = delims
        return [description]

    async def fake_menu(ctx, embeds, controls, timeout):
        captured["menu_embeds"] = embeds

    monkeypatch.setattr(translations_module, "pagify", fake_pagify)
    monkeypatch.setattr(translations_module, "menu", fake_menu)

    asyncio.run(translations_module.translations(cast(commands.Context, object())))

    assert captured["description"] == "** akjv ** - AKJV\n** bsb ** - BSB\n"
    assert captured["page_length"] == 3950
    assert captured["delims"] == ["```", "\n", "\n\n", "**"]
    assert captured["menu_embeds"][0].description == captured["description"]
