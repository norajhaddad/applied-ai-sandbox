"""Tests for the note-pinning feature (M7).

Reading stays public; notes are the in-memory app.notes list. Notes are
addressed by a stable id, not list position. New tests only — existing task
tests are untouched.
"""


def _add(app, title, body="body"):
    """Append a note the way new_note does and return its stable id."""
    note_id = app.next_note_id
    app.notes.append({"id": note_id, "title": title, "body": body, "pinned": False})
    app.next_note_id += 1
    return note_id


def test_pin_toggles_flag(client, app):
    app.notes.clear()
    nid = _add(app, "A")
    r = client.post(f"/notes/{nid}/pin")
    assert r.status_code in (302, 303)
    assert app.notes[0]["pinned"] is True
    client.post(f"/notes/{nid}/pin")
    assert app.notes[0]["pinned"] is False


def test_home_floats_pinned_to_top(client, app):
    app.notes.clear()
    _add(app, "AAA")
    bbb = _add(app, "BBB")
    # Pin the later note; it should now render above the earlier one.
    client.post(f"/notes/{bbb}/pin")
    body = client.get("/").data.decode()
    assert body.index("BBB") < body.index("AAA")


def test_home_does_not_mutate_note_order(client, app):
    app.notes.clear()
    _add(app, "First")
    second = _add(app, "Second")
    client.post(f"/notes/{second}/pin")
    client.get("/")
    # Display is sorted, but the underlying list keeps insertion order.
    assert [n["title"] for n in app.notes] == ["First", "Second"]


def test_pin_targets_by_id_not_position(client, app):
    app.notes.clear()
    first = _add(app, "First")
    _add(app, "Second")
    # Simulate the list being reordered (as a future delete/reorder would do);
    # ids are unchanged.
    app.notes.reverse()
    client.post(f"/notes/{first}/pin")
    # Only the note with id `first` (titled "First") should be pinned —
    # addressing is by id, not position, and note B is untouched.
    assert [n["title"] for n in app.notes if n.get("pinned")] == ["First"]


def test_unknown_id_returns_404(client, app):
    app.notes.clear()
    _add(app, "Only")
    assert client.post("/notes/999/pin").status_code == 404


def test_missing_pinned_key_treated_as_unpinned(client, app):
    app.notes.clear()
    # A note created before the feature existed — has an id but no "pinned" key.
    app.notes.append({"id": 0, "title": "Legacy", "body": "old"})
    r = client.get("/")
    assert r.status_code == 200
    assert b"Legacy" in r.data
    # Toggling must not KeyError, and should set pinned True.
    client.post("/notes/0/pin")
    assert app.notes[0]["pinned"] is True
