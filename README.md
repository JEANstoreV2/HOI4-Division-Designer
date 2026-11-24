# HOI4 Division Designer

A web app that replaces the manual spreadsheet work *Hearts of Iron IV*
players do by hand in the in-game division designer. Pick battalions,
support companies, regimental support, and the modifiers that affect them
(Research, Grand Doctrine, Officer Corps, Tank Designer, Terrain), and the
app computes the resulting division stats — organisation, soft attack,
production cost, and the rest — instead of you doing it on paper or in a
spreadsheet.

It also includes a save/compare library for named divisions, an AI-assisted
search that generates and ranks candidate divisions against a chosen stat
(optionally under constraints like a research-year cutoff or a required
battalion type), and a "Patch Impact Preview" that stages a hypothetical
balance change and shows its effect on every saved division before it's
applied for real.

## Disclaimer

This is an **unofficial, fan-made tool**. It is not affiliated with,
endorsed by, or sponsored by Paradox Interactive, and *Hearts of Iron IV*
and all related names, data, and assets are the property of Paradox
Interactive.

No copyrighted game files, art, audio, or text are included or
redistributed anywhere in this repository. The numeric stats and short
mechanical names used here were observed from the game (its own data files
and in-game tooltips/screenshots) and re-written from scratch as this
project's own, independently-structured data — the same category of thing
every community wiki, build calculator, or respec planner for this game
already does (including Paradox's own community wiki). Facts about how a
game behaves aren't protected by copyright the way a specific piece of
writing or a specific file is; this project only ever reproduces the
former, never the latter.

If you're a Paradox rights holder and have a concern about this project,
please open an issue and it'll be addressed promptly.

## Status

This project is under active, ongoing development. See `CLAUDE.md` and
`Activity_Log.md` for the full, dated build history, design decisions, and
what's still open — both are kept up to date every session and are more
detailed than this README needs to be.

## Tech stack

- **Backend:** Python + Flask
- **Templates:** Jinja2
- **Frontend:** plain HTML/CSS + vanilla JS (ES modules), no framework
- **Persistence:** SQLite (`instance/division_designer.db`, created
  automatically on first run)

## Running it locally

```
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000`.

Run the test suite with:

```
python -m pytest -q
```

## License

MIT — see [LICENSE](LICENSE). This covers the code in this repository
only; it does not grant any rights to Paradox Interactive's own game,
data, or assets (see the Disclaimer above).
