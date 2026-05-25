"""Tiny Flask app — applied-ai-sandbox.

Each task in tasks/ asks you to add or fix one piece. The tests in tests/
describe exactly what "done" means.
"""
from __future__ import annotations

from flask import Flask, render_template, request, redirect, url_for, abort


def parse_tags(raw: str) -> list[str]:
    """Split a comma-separated tag string into a clean list of tags.

    Trims surrounding whitespace from each tag and drops empty entries, so
    "work, , urgent " -> ["work", "urgent"]. Missing or empty input -> [].
    Order is preserved and duplicates are kept as-is.
    """
    return [tag.strip() for tag in (raw or "").split(",") if tag.strip()]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "sandbox-not-a-real-secret"

    # In-memory store for the sandbox. Resets on every restart, which is
    # fine for practice. Real apps use a database.
    app.notes: list[dict] = []  # type: ignore[attr-defined]
    # Monotonic id for stable note identity. List indices shift when notes are
    # added or removed (e.g. once TASK 02's delete lands), so routes address a
    # note by this id, never by its position in the list.
    app.next_note_id = 0  # type: ignore[attr-defined]

    @app.route("/")
    def home():
        # Pinned notes float to the top; a stable sort keeps insertion order
        # within each group. Sort a view for display — never mutate app.notes.
        # Each note carries its own id, so the pin button addresses it by id.
        notes_pinned_first = sorted(
            app.notes, key=lambda note: not note.get("pinned", False)
        )
        return render_template("home.html", notes=notes_pinned_first)

    @app.route("/notes/new", methods=["GET", "POST"])
    def new_note():
        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            body = (request.form.get("body") or "").strip()
            # TASK 01 will add validation here.
            app.notes.append(
                {
                    "id": app.next_note_id,
                    "title": title,
                    "body": body,
                    "pinned": False,
                    "tags": [],
                }
            )
            app.next_note_id += 1
            return redirect(url_for("home"))
        return render_template("new_note.html")

    @app.route("/notes/<int:note_id>/pin", methods=["POST"])
    def pin_note(note_id: int):
        """Toggle the pinned flag on the note with this id; pinning it again unpins it."""
        # Look up by stable id, not list position, so a pin click stays correct
        # even after the list is reordered or a note is deleted. Read pinned with
        # .get so a note missing the key (created before this feature) defaults
        # to unpinned.
        note = next((n for n in app.notes if n.get("id") == note_id), None)
        if note is None:
            abort(404)
        note["pinned"] = not note.get("pinned", False)
        return redirect(url_for("home"))

    # TASK 02 will add a /notes/<idx>/delete route here.

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
