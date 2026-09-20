#!/usr/bin/env python3
"""Append an entry to the site's Updates list (and bump data_date).

  python3 add_update.py "Title of what changed" "One-line note"            # dated today
  python3 add_update.py "Title" "Note" --date 2026-12-20                   # explicit date
  python3 add_update.py "Title" "Note" --score 7.4                         # also set overall score

Then run ./publish.sh
"""
import json, sys, datetime, pathlib, argparse

p = argparse.ArgumentParser()
p.add_argument("title"); p.add_argument("note", nargs="?", default="")
p.add_argument("--date", default=datetime.date.today().isoformat())
p.add_argument("--score", type=float)
p.add_argument("--keep-date", action="store_true", help="do not change meta.data_date")
a = p.parse_args()

f = pathlib.Path(__file__).resolve().parent / "content" / "site.json"
S = json.loads(f.read_text(encoding="utf-8"))
S["updates"].append({"date": a.date, "title": a.title, "note": a.note})
if not a.keep_date:
    S["meta"]["data_date"] = a.date
if a.score is not None:
    S["score"]["overall"] = a.score
f.write_text(json.dumps(S, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("added:", a.date, "—", a.title)
