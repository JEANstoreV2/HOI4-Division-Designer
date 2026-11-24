import json
import sqlite3
from pathlib import Path

# Session persistence (Phase 1, added 2026-10-06) - see Activity_Log.md and
# CLAUDE.md's Persistence section for the full design. Doesn't fit data/'s
# "pure data" or logic/'s "pure functions over data" conventions, since this
# is genuine stateful I/O - kept as its own top-level module instead.
#
# One row per state "section" (composition, research, doctrine, ...) rather
# than one big blob, so the frontend can auto-save just the section that
# actually changed instead of resending everything on every click - see
# static/js/persistence.js. Each section's own JSON shape is owned entirely
# by its source JS file (composition.js, research.js, ...); this module
# never interprets it, just stores and returns the raw string.
SCHEMA = """
CREATE TABLE IF NOT EXISTS current_state (
    section TEXT PRIMARY KEY,
    data TEXT NOT NULL
)
"""

# Persistence Phase 2 (added 2026-11-02) - named saves, separate from the
# single current_state row-per-section above. A save is one atomic JSON
# blob holding all 8 state sections at once (not split per-section like
# current_state), since a named save is always written/read/deleted as one
# unit, never patched piecemeal. saved_at is set server-side at write time
# (app.py) - never trust a client-supplied timestamp.
SAVED_DIVISIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS saved_divisions (
    name TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    saved_at TEXT NOT NULL
)
"""


def _connect(db_path):
    connection = sqlite3.connect(db_path)
    connection.execute(SCHEMA)
    connection.execute(SAVED_DIVISIONS_SCHEMA)
    return connection


def get_section(db_path, section):
    """The stored JSON-decoded value for one section, or None if nothing's
    been saved for it yet (a fresh install, or a section no event has fired
    for in this browser) - callers (app.py's GET /api/state) distinguish
    this from an empty-but-present section rather than guessing a default.
    """
    with _connect(db_path) as connection:
        row = connection.execute(
            "SELECT data FROM current_state WHERE section = ?", (section,)
        ).fetchone()
    return json.loads(row[0]) if row else None


def get_all_sections(db_path):
    """Every currently-stored section as {section: decoded_value} - missing
    sections are simply absent, not null-padded (see GET /api/state).
    """
    with _connect(db_path) as connection:
        rows = connection.execute("SELECT section, data FROM current_state").fetchall()
    return {section: json.loads(data) for section, data in rows}


def set_section(db_path, section, value):
    """Upserts one section's value (any JSON-serializable object - each
    source JS file owns its own shape, see the module header)."""
    with _connect(db_path) as connection:
        connection.execute(
            "INSERT INTO current_state (section, data) VALUES (?, ?) "
            "ON CONFLICT(section) DO UPDATE SET data = excluded.data",
            (section, json.dumps(value)),
        )


def clear_all_sections(db_path):
    """Backs the "Reset All" control - wipes every section at once, same
    as a fresh install, without deleting the database file itself."""
    with _connect(db_path) as connection:
        connection.execute("DELETE FROM current_state")


def list_saved_divisions(db_path):
    """Metadata only (name + saved_at, most recent first) - no data - so the
    saved-divisions list UI never pulls every full bundle just to render
    rows."""
    with _connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name, saved_at FROM saved_divisions ORDER BY saved_at DESC"
        ).fetchall()
    return [{"name": name, "saved_at": saved_at} for name, saved_at in rows]


def get_saved_division(db_path, name):
    """The full saved bundle (every state section at save time) plus its own
    saved_at, or None if no save exists under this name."""
    with _connect(db_path) as connection:
        row = connection.execute(
            "SELECT data, saved_at FROM saved_divisions WHERE name = ?", (name,)
        ).fetchone()
    return {"data": json.loads(row[0]), "saved_at": row[1]} if row else None


def save_division(db_path, name, data, saved_at):
    """Upserts a named save - re-saving an existing name overwrites both its
    data and saved_at, matching Tank Designer's own overwrite-on-resave
    precedent for a saved design."""
    with _connect(db_path) as connection:
        connection.execute(
            "INSERT INTO saved_divisions (name, data, saved_at) VALUES (?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET data = excluded.data, saved_at = excluded.saved_at",
            (name, json.dumps(data), saved_at),
        )


def delete_saved_division(db_path, name):
    """A no-op (not an error) if name doesn't exist - same tolerance
    clear_all_sections already has for an empty table."""
    with _connect(db_path) as connection:
        connection.execute("DELETE FROM saved_divisions WHERE name = ?", (name,))


def ensure_db_directory(db_path):
    """Call once at startup (app.py) - sqlite3.connect doesn't create the
    parent directory (Flask's instance/ folder) on its own."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
