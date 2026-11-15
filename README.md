# Marswalk: a crew-and-rover route planner and tablet for Mount Sharp

NASA Space Apps Challenge 2026 · challenge: **Interplanetary Survival Guide: Martian Map** · team: Employees of the Month

**In one paragraph.** Two agents leave a habitat on Mars: an astronaut on foot and a rover carrying gear. They cannot go the same places, so each gets its own terrain-cost map built from real HiRISE data. The planner finds a route for each, picks three science stops, checks that everyone stays inside an abort radius, and estimates the radiation dose of the excursion. A tablet page shows all of it: map layers, a 3D terrain view, a route profile, a radiation panel with a solar-storm what-if, and a simulated rover-camera view.

**Live tablet page:** [gab-lap.github.io/marswalk-martian-map](https://gab-lap.github.io/marswalk-martian-map/) · **Demo deck:** [PDF on Google Drive](https://drive.google.com/file/d/1X8OpwYs5yQFLQSyO_yOjhOQOBsApU7H3/view?usp=sharing) · **NASA Space Apps team:** Employees of the Month

**Jump to:** [Results](#results-on-the-real-window) · [How it works](#how-it-works) · [What the tablet shows](#what-the-tablet-shows) · [Assumptions](#assumptions-you-should-know-about) · [Known limitations](#known-limitations) · [Run it yourself](#run-it-yourself) · [Use of AI](#use-of-ai)

You do not need to install anything to see it:
- Tablet page (clickable, runs in the browser): `docs/index.html` (or the GitHub Pages link)
- Map pack: `docs/map_pack/` (`1_layers.png`, `2_costs.png`, `3_routes.png`, `4_ortho_masks.png`)

## The idea

The Martian Map challenge asks for a layered map that helps a crew plan a Marswalk. Existing tools show Mars in layers at coarse scale. What was missing for us was the meter-scale step: given real terrain, where can a person walk, where can a rover drive, and where do they meet?

- **The astronaut** walks up to 25° slopes, avoids rocks, and pays extra to cross ridges and soft hollows.
- **The rover** drives up to 15° slopes, never crosses ridges, and pays a lot to cross soft hollows.
- **The rover** drives to the edge of the lattice (Stop 1) and leaves gear there. For Stops 2 and 3 it goes to the nearest ground it can reach and waits; the astronaut walks the remaining gap on foot (the tablet shows the gap for each stop), then returns. The rover drives back to the habitat after the last stop.
- **The abort radius** is 400 m from the habitat; every route must stay inside it.

## Site and data

The site is the boxwork area on Mount Sharp, Gale Crater, a honeycomb pattern of ridges and hollows that Curiosity has been studying. The planner uses a 500 × 500 m window (column 3300, row 10450) of:

| Data | What it is | Used for |
|---|---|---|
| HiRISE DTM `DTEEC_001488_1750_001752_1750_U02` (MRO, University of Arizona / PDS archive), 1 m per cell | Elevation | Slope, rocks, route heights, 3D terrain |
| HiRISE RED orthoimage `PSP_001752_1750_RED_C_01_ORTHO` | Brightness photo of the same ground | Ridge and hollow masks, 3D texture |
| MSL RAD (Curiosity radiation instrument), first-year summary, about 210 µGy/day | Surface radiation rate | Dose estimate (8.75 µGy/h) |

**Important limit:** the 1 m DTM does not resolve the boxwork lattice. The ridge and hollow layers therefore come from the *orthoimage brightness* (light = ridge, dark = hollow). That is a proxy, not elevation, and shadows can fool it. Slopes and mobility limits still come from the DTM. The rock layer is thin.

## How it works

1. **Load** the DTM and orthoimage window (`marswalk/terrain.py`).
2. **Masks:** find hollows as compact dark blobs, mark the lattice zone where they are dense, and keep ridges only inside it.
3. **Costs:** one cost grid per agent from slope, ridges, hollows and rocks (`marswalk/costs.py`, limits in `marswalk/params.py`).
4. **Stops:** rule-based habitat and three stops (`marswalk/stops.py`). These are rules on proxy layers, not a scientific selection.
5. **Routes:** A* on each grid, no corner-cutting (`marswalk/planner.py`).
6. **Report:** per-point profile, radiation scenarios and labelled numbers into `routes.json` (`marswalk/report.py`), plus layer images and a height grid (`marswalk/layers.py`).
7. **Nav2:** the rover cost grid is exported as `rover_cost.pgm/.yaml` and tested in ROS 2 Nav2 (`nav2_test/`). Nav2 plans with its own cost scaling and inflation, so its path length differs from the A* length.
8. **Tablet:** `tools/build_tablet.py` injects `routes.json` into `tablet/template.html` to produce a standalone browser page (`docs/index.html`).

## Results on the real window

| Item | Value | Label |
|---|---|---|
| Astronaut route | 565 m, max slope 17.6°, farthest point 232 m from the habitat | derived |
| Walking time | 9.4 min at 1.0 m/s | speed assumed |
| Time at stops | 3 × 15 min (54.4 min total) | assumed |
| Excursion dose | 7.9 µGy for 54 min, verdict GO | rate sourced, time assumed |
| Excursion limit | 50 µGy | assumed (no official EVA limit used) |
| Rover route | 605 m, max slope 14.2°, 20.2 min at 0.5 m/s, farthest point 225 m from the habitat; goes to Stop 1, then to the nearest reachable ground for Stops 2 and 3, and returns to the habitat | derived, speed assumed |
| Rover battery | 99.8% at the rendezvous | simulated |

Habitat at (row 32, col 110); stops at (62, 157), (112, 239), (229, 228) in the window.

Every number in `routes.json` and on the tablet carries one of four labels: **sourced** (a NASA dataset), **derived** (computed from the data or the route), **assumed** (our parameter) or **simulated** (invented for illustration).

## Assumptions you should know about

All of them live in `marswalk/params.py`.

- Slope limits (astronaut 25°, rover 15°), ridge and hollow penalties, walking speed 1.0 m/s, rover speed 0.5 m/s.
- Abort radius 400 m and the 50 µGy excursion limit.
- Dwell time 15 min per stop, rover camera height 1.6 m, and the rover returning to the habitat at the end.
- The solar-storm slider multiplies the dose up to 60×. It is a **hypothetical stress test**, not from RAD data: the largest event in the first-year summary was only a modest rise over normal. At the current route time the verdict flips around 6×.
- Rover battery drain is invented for the mockup.
- The rover cannot cross the lattice ridges. It visits every stop it can reach and otherwise waits at the nearest reachable ground; the distance left to walk is reported per stop (`rover_gap_m` in `routes.json`).

## What the tablet shows

- **Map** with the astronaut route, rover route, habitat, stops and the abort ring, with toggles for hillshade, slope and the ortho masks.
- **3D view:** the DTM as a mesh with the orthoimage draped over it. Heights can be exaggerated ×1 to ×3. The mesh shows the DTM only, so the honeycomb appears through the photo, not in the shape.
- **Route profile** with elevation and slope, a position slider, next-stop distance and ETA.
- **Radiation panel** with the dose against the limit, the solar-storm slider and a NO-GO banner.
- **Rover camera:** a *simulated* view rendered from the DTM at the rover, not a real camera image.
- **Tabs** (Mission, Safety, Rover) keep the side panel short. The next stop, the position slider and any NO-GO banner stay visible above them. The Safety tab also shows the time left before the dose limit and the abort margin (both derived).

## Run it yourself

Tested on Ubuntu 24.04 with Python 3. A virtual environment is needed there, because a plain `pip install` is blocked on that system.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy scipy matplotlib rasterio

python3 run_demo.py out                                   # synthetic test terrain, not Mars
python3 run_demo.py out \
  --dtm DTEEC_001488_1750_001752_1750_U02.IMG \
  --ortho PSP_001752_1750_RED_C_01_ORTHO.JP2              # real window
python3 tools/build_tablet.py out/routes.json docs/index.html
```

Open `docs/index.html` in a browser (the 3D view loads three.js from cdnjs, so it needs internet), or open `tablet/template.html` and use "Load routes.json". The DTM and orthoimage are large; get them from the HiRISE archive (University of Arizona) and do not commit them. `tools/` has helpers to check a window and tune the masks (`tune_masks.py`).

## Repository layout

```text
marswalk/      planner: terrain, costs, stops, planner, report, layers, viz, export
nav2_test/     loads rover_cost.* in Nav2's planner server (ROS 2 Jazzy)
tablet/        the page template (single HTML file)
tools/         window checks, mask tuning, build_tablet.py
docs/          built tablet page (GitHub Pages) and the map pack
run_demo.py    the whole pipeline
CHANGELOG.md   version history and notes
```

## Known limitations

- Ridges and hollows are a brightness proxy; the lattice zone is conservative and misses a strip of weaker lattice on the left of the window.
- Stops and the habitat follow simple rules and were checked by eye on the overlay.
- The Nav2 and RViz results are from our own run; judges do not need ROS to see the results (map pack and tablet).
- The page is a static prototype. The planner runs offline and the page displays its exports; there is no live backend.
- Not done: re-planning when conditions change, a walking-astronaut view, real RAD data pulled from the PDS.

## Use of AI

Some code in this repository was written with the help of Claude (Anthropic) and Gemini (Google), primarily the frontend. A UI mockup generated with AI was used as a visual reference starting point when designing the tablet page; the page in `tablet/` is a separate implementation. All results shown were produced by running the code; all the AI-written text and code were reviewed by the team. No NASA logos or mission identifiers appear in generated content.

## References

- HiRISE DTM and orthoimage, NASA/JPL/University of Arizona, Mars Reconnaissance Orbiter (HiRISE archive).
- MSL RAD first-year radiation summary: Hassler et al., "Mars' surface radiation environment measured with the Mars Science Laboratory's Curiosity rover", Science, 2014 (rate not re-checked against the PDS archive).
- Software: Python, NumPy, SciPy, Matplotlib, rasterio, three.js (r128, cdnjs), ROS 2 Jazzy and Nav2, RViz2.
- Gemini (Google) and Claude (Anthropic) as AI tools, as described above.

## License

MIT, see `LICENSE`. Data belongs to its providers.