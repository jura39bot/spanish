#!/usr/bin/env python3
"""Build index.html from src/template.html + src/data.json (single-file PWA)."""
import json, pathlib, hashlib, datetime

root = pathlib.Path(__file__).parent
tpl = (root / "src/template.html").read_text(encoding="utf-8")
data = json.loads((root / "src/data.json").read_text(encoding="utf-8"))
for extra_path in sorted((root / "src").glob("extra*.json")):
    extra = json.loads(extra_path.read_text(encoding="utf-8"))
    for lvl, items in extra.items():
        seen = {i["e"] for i in data.get(lvl, [])}
        data.setdefault(lvl, [])
        data[lvl].extend([i for i in items if i["e"] not in seen])

# merged corpus, shared with daily.py
(root / "src/all.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
conj = json.loads((root / "src/conj.json").read_text(encoding="utf-8")) if (root / "src/conj.json").exists() else []
quest = json.loads((root / "src/questions.json").read_text(encoding="utf-8")) if (root / "src/questions.json").exists() else []
gram = json.loads((root / "src/grammar.json").read_text(encoding="utf-8")) if (root / "src/grammar.json").exists() else []
conv = json.loads((root / "src/conversations.json").read_text(encoding="utf-8")) if (root / "src/conversations.json").exists() else []
lex_ = json.loads((root / "src/lexique.json").read_text(encoding="utf-8")) if (root / "src/lexique.json").exists() else {"categories":[]}
build = datetime.datetime.now().strftime("%Y%m%d.%H%M")
html = (tpl.replace("__DATA__", compact)
           .replace("__CONJ__", json.dumps(conj, ensure_ascii=False, separators=(",", ":")))
           .replace("__QUEST__", json.dumps(quest, ensure_ascii=False, separators=(",", ":")))
           .replace("__LEX__", json.dumps(lex_, ensure_ascii=False, separators=(",", ":")))
           .replace("__CONV__", json.dumps(conv, ensure_ascii=False, separators=(",", ":")))
           .replace("__GRAM__", json.dumps(gram, ensure_ascii=False, separators=(",", ":")))
           .replace("__BUILD__", build))
# STRUCTURE CHECK — refuse de publier une page blanche
for tag in ("style","script","body"):
    o = html.count("<"+tag+">") if tag!="body" else html.count("<body>")
    c = html.count("</"+tag+">")
    if tag in ("style","script") and o != c:
        raise SystemExit(f"STRUCTURE CHECK FAILED: <{tag}> {o} / </{tag}> {c}")
if html.count("<body>") != 1:
    raise SystemExit("STRUCTURE CHECK FAILED: body missing")

(root / "index.html").write_text(html, encoding="utf-8")

total = sum(len(v) for v in data.values())
print(f"index.html {len(html)} bytes — {total} items, {len(conj)} verbes, {len(quest)} questions — build {build}")
for k, v in data.items():
    print(f"  {k}: {len(v)}")
print("sha", hashlib.sha256(html.encode()).hexdigest()[:12])
