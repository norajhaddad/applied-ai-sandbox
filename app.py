"""Tiny Flask app — applied-ai-sandbox.

Each task in tasks/ asks you to add or fix one piece. The tests in tests/
describe exactly what "done" means.
"""
from __future__ import annotations

from flask import Flask, render_template, request, redirect, url_for, abort


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "sandbox-not-a-real-secret"

    # In-memory store for the sandbox. Resets on every restart, which is
    # fine for practice. Real apps use a database.
    app.notes: list[dict] = []  # type: ignore[attr-defined]

    @app.route("/")
    def home():
        # Pinned notes float to the top. Sort a view (never mutate app.notes)
        # and carry each note's original index so the pin button targets the
        # right note even after the list is reordered for display.
        ordered = sorted(
            enumerate(app.notes),
            key=lambda item: not item[1].get("pinned", False),
        )
        return render_template("home.html", notes=ordered)

    @app.route("/notes/new", methods=["GET", "POST"])
    def new_note():
        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            body = (request.form.get("body") or "").strip()
            # TASK 01 will add validation here.
            app.notes.append({"title": title, "body": body, "pinned": False})
            return redirect(url_for("home"))
        return render_template("new_note.html")

    @app.route("/notes/<int:idx>/pin", methods=["POST"])
    def pin_note(idx: int):
        # Toggle pinned on the note at this index. Single endpoint: pinning an
        # already-pinned note unpins it. Read with .get so a note missing the
        # key (created before this feature) is treated as unpinned.
        if idx < 0 or idx >= len(app.notes):
            abort(404)
        note = app.notes[idx]
        note["pinned"] = not note.get("pinned", False)
        return redirect(url_for("home"))

    # TASK 02 will add a /notes/<idx>/delete route here.

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
