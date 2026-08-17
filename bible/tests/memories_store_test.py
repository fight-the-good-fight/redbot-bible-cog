import json

from bible import memories_store


def test_load_memories_missing_file_returns_empty(tmp_path):
    assert memories_store.load_memories(tmp_path / "nope.json") == []


def test_load_memories_reads_list(tmp_path):
    p = tmp_path / "memories.json"
    notes = [{"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "hi"}]
    p.write_text(json.dumps(notes), encoding="utf-8")
    assert memories_store.load_memories(p) == notes


def test_load_memories_invalid_json_returns_empty(tmp_path):
    p = tmp_path / "memories.json"
    p.write_text("{not json", encoding="utf-8")
    assert memories_store.load_memories(p) == []


def test_load_memories_non_list_returns_empty(tmp_path):
    p = tmp_path / "memories.json"
    p.write_text(json.dumps({"Notes": []}), encoding="utf-8")
    assert memories_store.load_memories(p) == []


def test_save_memories_writes_list(tmp_path):
    p = tmp_path / "memories.json"
    notes = [{"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "hi"}]
    memories_store.save_memories(notes, p)
    assert json.loads(p.read_text(encoding="utf-8")) == notes


def test_save_memories_creates_parent_dirs(tmp_path):
    p = tmp_path / "nested" / "dir" / "memories.json"
    memories_store.save_memories([], p)
    assert p.exists()
    assert json.loads(p.read_text(encoding="utf-8")) == []


def test_round_trip(tmp_path):
    p = tmp_path / "memories.json"
    notes = [
        {"number": 1, "book": "Genesis", "chapter": 1, "verse": 1, "note": "a"},
        {"number": 2, "book": "Exodus", "chapter": 2, "verse": 3, "note": "b"},
    ]
    memories_store.save_memories(notes, p)
    assert memories_store.load_memories(p) == notes


def test_memories_path_uses_cog_data_dir(monkeypatch, tmp_path):
    from redbot.core import data_manager

    monkeypatch.setattr(
        data_manager,
        "basic_config",
        {"DATA_PATH": str(tmp_path), "COG_PATH_APPEND": "cogs"},
    )
    p = memories_store.memories_path()
    assert p.parent.name == "Bible"
    assert p.name == "memories.json"
    assert p.parent.is_dir()