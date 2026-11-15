"""Builds the clickable tablet page with YOUR routes.json inside it (one self-contained HTML file).
  python3 tools/build_tablet.py out/routes.json docs/index.html
docs/index.html can be served by GitHub Pages (Settings > Pages > Deploy from branch > main /docs)."""
import json, sys, os
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))
for k in ("astronaut", "rover"):                      # keep the page light: every 3rd route point (the page interpolates)
    p = d[k]["points"]; d[k]["points"] = p[::3] + ([p[-1]] if (len(p) - 1) % 3 else [])
tpl = open(os.path.join(os.path.dirname(__file__), "..", "tablet", "template.html")).read()
os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
open(dst, "w").write(tpl.replace("__DATA__", json.dumps(d, separators=(",", ":"))))
print("wrote", dst, round(os.path.getsize(dst) / 1e6, 2), "MB; terrain source:", d["meta"]["terrain_source"])
