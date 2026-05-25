"""Tests for the note-pinning feature (M7).

Reading stays public; notes are the in-memory app.notes list. New tests only —
existing task tests are untouched.
"""


def _add(app, title, body="body"):
    app.notes.append({"title": title, "body": body, "pinned": False})


def test_pin_toggles_flag(client, app):
    app.notes.clear()
    _add(app, "A")
    r = client.post("/notes/0/pin")
    assert r.status_code in (302, 303)
    assert app.notes[0]["pinned"] is True
    client.post("/notes/0/pin")
    assert app.notes[0]["pinned"] is False


def test_home_floats_pinned_to_top(client, app):
    app.notes.clear()
    _add(app, "First")
    _add(app, "Second")
    # Pin the later note; it should now render above the earlier one.
    client.post("/notes/1/pin")
    body = client.get("/").data.decode()
    assert body.index("Second") < body.index("First")


def test_home_does_not_mutate_note_order(client, app):
    app.notes.clear()
    _add(app, "First")
    _add(app, "Second")
    client.post("/notes/1/pin")
    client.get("/")
    # Display is sorted, but the underlying list keeps insertion order.
    assert [n["title"] for n in app.notes] == ["First", "Second"]


def test_invalid_index_returns_404(client, app):
    app.notes.clear()
    _add(app, "Only")
    assert client.post("/notes/5/pin").status_code == 404


def test_missing_pinned_key_treated_as_unpinned(client, app):
    app.notes.clear()
    # A note created before the feature existed — no "pinned" key at all.
    app.notes.append({"title": "Legacy", "body": "old"})
    r = client.get("/")
    assert r.status_code == 200
    assert b"Legacy" in r.data
    # Toggling must not KeyError, and should set pinned True.
    client.post("/notes/0/pin")
    assert app.notes[0]["pinned"] is True
