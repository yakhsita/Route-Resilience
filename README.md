# Route Resilience

**Uncertainty-Aware Road Network Reconstruction, Live Road-Status Integration & Emergency Accessibility Analysis**

**Timeline:** 6 weeks / 42 days  
**Team:** 3 developers  
**Deliverable:** Working, reproducible software prototype with satellite road extraction, inferred links, road-network criticality, *source-attributed current road status*, dynamic route recalculation, and a polished dashboard.

> **Scope and honesty:** “Real-time” means **automatically refreshed data from an actual provider**, with measured update delay and coverage. It does **not** mean satellite video or universal detection of every blocked road. Road imagery and reconstructed links do not prove that roads are passable. A feed with no events does not mean all roads are open. Do not use this student prototype for real emergency dispatch.

## 1. What the final demo should show

1. Select a study area and display its satellite image.
2. Toggle the AI-predicted road mask, observed road graph, and **inferred** missing connections.
3. Highlight important road links and inspect criticality scores.
4. Turn on a **Live/Reported Events** layer with provider, event type, report time, last fetched time, and freshness.
5. Show road status as **reported closed**, **reported restricted**, **unknown/unreported**, or **simulated closed**; never infer “open” from missing reports.
6. When a new event matches a graph edge, mark that edge affected and recalculate the route and accessibility metrics.
7. Show before/after path distance or cost, affected destinations, and a clear explanation of what changed.
8. Let the user manually simulate a closure for comparison, clearly separated from provider reports.
9. If the provider is unavailable, show **feed unavailable / stale** and allow a replay of previously recorded, attributed events for demonstration.

### Target pipeline

```text
Satellite imagery + permitted road labels
     -> segmentation (U-Net baseline)
     -> observed road mask + gap proposals + uncertainty
     -> road graph (nodes, edges, georeferencing when available)
                           |
Live road-status provider -> event adapter -> map-match event to graph edges
                           |
               status overlay + graph update
                           |
      Dijkstra / connectivity / criticality / accessibility
                           |
           Streamlit map + scenario dashboard
```

## 1A. Technical direction from the ISRO BAH 2026 submission PDF

The team's submitted slide deck (`yak_ps.pdf`, pp. 3–10) is a useful design reference. Its challenge framing is **“Route Resilience — Occlusion-Robust Road Extraction & Graph-Theoretic Criticality Analysis for Urban Mobility.”** It proposes a four-stage concept: **see through occlusions → repair road topology → rank gatekeepers and stress-test failures → interactive planner dashboard**. The live-road-status module is an **additional requirement from our project guide**, not something demonstrated as already implemented in the PDF.

### How the presentation changes our implementation

| Deck concept | Practical implementation | Priority |
|---|---|---|
| Optical + SAR fusion for occlusion robustness (pp. 3, 5, 8) | Start with optical U-Net baseline. Investigate *paired, co-registered, suitably resolved and licensed* optical/SAR imagery. Only add SAR if actual matching data exists and measurable improvement is possible. SAR does not automatically reveal individual roads under every canopy. | Research/stretch |
| Topology-aware road reconstruction (pp. 3–6) | Extract endpoints and junctions; propose candidate links; check distance, direction, imagery evidence, confidence, and ground truth. Compare graph connectivity before/after. | Core |
| MST + Disjoint Set healing loop (p. 6) | Use union-find to identify disconnected components and MST/minimum-cost candidate-link selection **only among plausible candidates**. Never force all components to connect: genuine dead ends and separated roads exist. | Core experiment |
| Betweenness “gatekeepers” (pp. 5–6) | Calculate edge/node betweenness and identify articulation points and bridges; validate importance by removing edges/nodes and measuring accessibility impact. | Core |
| Node ablation + Resilience Index (p. 6) | Test single-node and single-edge failures, plus selected multiple-failure scenarios. Define the index explicitly (e.g. fraction of reachable essential destinations or reachable origin–destination pairs), record denominator and weights. | Core |
| DEM-based flood simulation (pp. 3, 5) | Add a separate **illustrative terrain-based hazard scenario** only if DEM, road elevations, water-level assumptions, and alignment are available. A DEM alone cannot predict actual flooding or confirm closures. | Stretch |
| Dashboard mockup (p. 7) | Use the slide's layout as a visual reference: left-side layer controls, center road graph/map, right-side resilience metrics, bottom before/after plot. Rebuild rather than treating the mockup as working software. | Core |
| Four-layer architecture (p. 8) | Data → extraction → graph → analytics/dashboard; extend with an independent **live event ingestion and matching** branch. | Core |
| Proposed Next.js/FastAPI/PostgreSQL/Redis stack (p. 9) | Treat as a possible production architecture, **not a six-week requirement**. Streamlit + NetworkX + lightweight API polling is simpler for three laptops. | Later |
| ₹12,500 indicative budget (p. 10) | A slide estimate, **not a confirmed cost**. Use local RTX 3050 and free/open tools first; validate provider costs and licenses before spending. | Planning |

**Source boundary:** The PDF is a proposed pitch/deck, not evidence that the listed algorithms, datasets, API coverage, accuracy, or flood forecasts already work. It mentions Sentinel-2, Cartosat, SAR, OSM and DEM; the precise availability, spatial resolution, alignment, and permitted usage of each dataset must be checked independently. The satellite image shown on p. 4 is an explanatory example, not a verified training pair.

### Revised research question and defensible novelty

> Can occlusion-aware, uncertainty-scored topology repair improve the correctness of extracted road-network connectivity, and can graph-failure analysis combined with **source-attributed current road-status reports** improve planners' awareness of critical access disruptions?

Evaluate **three separate contributions**: (1) road-mask/topology accuracy, (2) criticality and resilience sensitivity to failures, and (3) timeliness and correctness of provider-attributed event-to-road updates. Do not claim a single unmeasured end-to-end improvement.

## 2. Team and laptop allocation

| Owner | Laptop | Primary responsibility | Deliverables |
|---|---|---|---|
| **You: ML + integration lead** | i5-13450HX, 16 GB RAM, RTX 3050 6 GB | Dataset, U-Net segmentation, occlusion experiments, graph/imagery alignment, integration and release | `road_mask.png`, `inferred_links.json`, model weights, evaluation report |
| **Teammate 1: graph + live-feed backend** | i5-8250U, 16 GB RAM, Intel UHD 620 | Graph construction, Dijkstra, criticality, live API adapter, map matching, status update logic | `road_graph.geojson` or JSON, normalized events, routing and incident tests |
| **Teammate 2: dashboard + QA** | i3-1115G4, 4 GB RAM, integrated graphics | Streamlit, overlays, event badges, status freshness, controls, presentation and end-to-end tests | Dashboard and demo workflow |

All teammates work from small **mock fixtures** immediately; live data access and ML training must not block other modules.

## 3. The real-time data decision: do this in Week 1

A reliable live module needs a **provider that actually covers the chosen study area**. Choose the study area and verify the feed *before* promising live closures. Potential categories:

- **Authorized traffic incident / road-closure API** (commercial or government): may report closures, construction, restrictions, accidents; check exact coverage, access requirements, pricing, quotas, and permitted display/redistribution.
- **City traffic police / municipal official alerts:** useful if published as a machine-readable, permitted feed; a social media page or press release is **not automatically a usable real-time API**.
- **Flood / hazard alerts:** can be an additional risk overlay but **must not automatically be treated as confirmed road closures**.
- **Recorded events for replay:** a transparent fallback for a live-like demonstration; label it **REPLAY / HISTORICAL**, never LIVE.

**Candidate providers to evaluate, not guaranteed integrations:** TomTom Traffic Incidents, HERE Traffic, and any documented local government traffic feed. Verify actual API availability and terms for your selected area. Google Maps consumer UI is not a freely reusable live road-closure dataset.

### Provider acceptance checklist

- [ ] The provider offers an authorized API or downloadable feed.
- [ ] It has **actual closure/incident examples** in our selected city/area.
- [ ] It exposes coordinates/geometry and an event type/status.
- [ ] Timestamps are available or the limitations are clearly documented.
- [ ] We can refresh within its quota and terms.
- [ ] We can display or store the necessary fields under its license.
- [ ] We tested an actual request and saved a **redacted** sample response.
- [ ] We documented a fallback if the feed has no active events.

**Go/no-go by Day 7:** If no suitable authorized feed covers the selected area, either (a) choose another supported demonstration area, or (b) present **historical event replay plus live polling infrastructure** and explicitly say real-time closure coverage is unverified. Do not silently substitute simulations for live data.

## 4. Six-week schedule (42 days)

### Week 1 — Project setup, feasibility, and API proof (Days 1–7)

**ML lead:** Set up repo and Python; select a permitted high-resolution road dataset; inspect masks and georeferencing; build image loader; check whether paired optical/SAR data is actually feasible.  
**Graph/live lead:** Build a synthetic 10–20-node graph; implement Dijkstra; investigate and test provider access for the target study area; record response schema and coverage.  
**UI lead:** Build Streamlit shell with image, layers, event panel, and a clearly labeled simulated closure button.

**Gate:** At least one working synthetic reroute; provider selection documented with evidence; sample event JSON normalized (live or recorded).

### Week 2 — Baseline AI + road graph (Days 8–14)

**ML lead:** Train or fine-tune lightweight U-Net on small image tiles (start with 256×256, batch size 2–4 as memory permits); save road masks and metrics.  
**Graph/live lead:** Implement skeleton-to-graph conversion and edge removal; create provider adapter interface and parser with mocked responses.  
**UI lead:** Add observed road mask and graph overlay, route selectors, criticality cards, and mock events.

**Gate:** Image -> mask -> graph -> route on a reproducible small study tile. Mock event -> edge status -> reroute also works.

### Week 3 — Reconstruction + graph criticality (Days 15–21)

**ML lead:** Simulate occlusion over known roads; propose missing links; store **heuristic** confidence and evaluate false positives.  
**Graph/live lead:** Add bridges, articulation points, edge/node betweenness, node ablation, edge-removal impact, connectivity, and emergency-destination reachability; test union-find/MST on plausible link candidates.  
**UI lead:** Add confidence filter, observed/inferred legend, critical-road ranking, before/after comparison, and a clearly defined resilience-index panel.

**Gate:** Demonstrate reconstruction against known hidden roads, candidate-link rejection, edge/node failure analysis, and one simulated closure with measured connectivity effects. Do **not** connect components just to make the graph fully connected.

### Week 4 — Live status integration (Days 22–28)

**Graph/live lead (primary):** Implement actual authorized provider request, normalization, polling with a documented interval, deduplication, timestamps, event expiry, and event-to-road map matching. Store API credentials in environment variables.  
**ML lead:** Align the road graph to geographic coordinates **only when source imagery has valid georeferencing**; help validate map matching; otherwise use an independently georeferenced base graph for the live layer and document that choice.  
**UI lead:** Display provider attribution, last updated time, stale-feed warning, and event geometry; add a manual refresh control.

**Gate:** A real provider request (if available) reaches the UI and updates graph edge states. No fabricated live events.

### Week 5 — Dynamic routing and robustness (Days 29–35)

- Event status -> affected edges -> shortest-path recalculation.
- Recompute emergency accessibility and criticality impact after event updates.
- Avoid falsely closing a whole road when an incident point has ambiguous location: mark as **unmatched / needs review**.
- Support multiple incidents, duplicate updates, API timeouts, empty responses, and expired events.
- Add optional incident replay mode for deterministic demos.
- Compare routing before/after events; log fetch latency and freshness.

**Gate:** Reproducible end-to-end demonstration for live provider data **or explicitly labeled replay**, plus automated tests.

### Week 6 — Evaluation, report, and polished presentation (Days 36–42)

- **Days 36–38:** Quantitative ML and graph evaluation (including no-repair vs heuristic repair, false connections, node ablation and defined resilience index); incident map-matching accuracy; feed latency/freshness tests; edge cases.
- **Days 39–40:** Fix UX, prepare architecture diagrams, screenshots, video, installation instructions, and slides.
- **Day 41:** Feature freeze and clean-install rehearsal on teammate's machine.
- **Day 42:** Final presentation and release tag.

**Fallback rule:** If AI training underperforms, use a **clearly labeled reference road mask** for graph demonstration; if the live API is unavailable, demonstrate honest recorded replay and report the limitation.

## 5. Recommended stack

| Area | Tools |
|---|---|
| Language | Python 3.11 |
| Road segmentation | PyTorch + lightweight U-Net |
| Image processing | OpenCV, scikit-image, NumPy |
| Graph | NetworkX, Dijkstra, bridges, centrality |
| Geospatial | Rasterio, GeoPandas/Shapely as needed, GeoJSON |
| Live feed | Provider REST API, `httpx` or `requests`, polling |
| Dashboard | Streamlit + Plotly or Folium |
| Tests | pytest + mocked API responses |
| Collaboration | GitHub pull requests |

**Keep the MVP simple:** No React, Redis, PostgreSQL, Docker, or Kafka unless an actual requirement arises. For a small demo, a single process can poll on a controlled interval; avoid one poller per Streamlit session. Observe provider rate limits.

## 6. Repository structure (planned)

```text
route-resilience/
├── README.md
├── .gitignore
├── .env.example
├── requirements-base.txt
├── requirements-ml.txt
├── app/
│   └── dashboard.py
├── src/
│   ├── ml/
│   │   ├── preprocess.py
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── reconstruct.py
│   ├── graph/
│   │   ├── build_graph.py
│   │   ├── routing.py
│   │   ├── criticality.py
│   │   ├── topology_repair.py
│   │   └── resilience.py
│   ├── live/
│   │   ├── provider.py
│   │   ├── normalize.py
│   │   ├── map_match.py
│   │   └── refresh.py
│   └── common/
│       └── schemas.py
├── data/
│   └── samples/
├── tests/
│   ├── test_topology_repair.py
│   ├── test_node_ablation.py
│   ├── test_resilience_index.py
│   ├── test_routing.py
│   ├── test_criticality.py
│   ├── test_live_normalize.py
│   ├── test_map_match.py
│   └── test_feed_freshness.py
├── outputs/
├── models/
└── docs/
    ├── provider_feasibility.md
    ├── evaluation.md
    ├── demo_script.md
    └── decisions.md
```

These are **proposed modules**; the README does not imply that the code already exists.

## 7. Setup for each teammate

Install Python 3.11, Git, and VS Code. Clone the repository after the team creates it:

```bash
git clone https://github.com/YOUR-ORG/route-resilience.git
cd route-resilience
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Update pip and install the lightweight stack:

```bash
python -m pip install --upgrade pip
pip install numpy opencv-python-headless scikit-image networkx pandas pillow streamlit plotly requests httpx pytest
```

ML lead only: install PyTorch using the official OS/CUDA-specific selector at <https://pytorch.org/get-started/locally/>. Test:

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

After implementation, run:

```bash
streamlit run app/dashboard.py
pytest -q
```

### Credentials

Use `.env` or local environment variables. Example `.env.example`:

```dotenv
TRAFFIC_PROVIDER=your_authorized_provider
TRAFFIC_API_KEY=REPLACE_ME
TRAFFIC_POLL_SECONDS=300
STUDY_AREA=choose_a_supported_area
```

The 300-second interval is an **example**, not a promise of five-minute data freshness. Confirm permitted polling frequency, quotas, and timestamps with the chosen provider. Never commit real keys.

## 8. Shared data contracts

### `road_mask.png`

Single-channel image; `0` = background and `255` = road. Same dimensions as source image. Save segmentation threshold/model version separately.

### `road_graph.json` (example)

```json
{
  "coordinate_system": "pixel",
  "image_width": 512,
  "image_height": 512,
  "nodes": [
    {"id": "A", "x": 20, "y": 30},
    {"id": "B", "x": 110, "y": 30}
  ],
  "edges": [
    {"id": "AB", "source": "A", "target": "B",
     "length_pixels": 90, "origin": "observed", "confidence": null}
  ]
}
```

### `inferred_links.json` (example)

```json
{
  "links": [
    {"source": "B", "target": "C", "origin": "inferred",
     "confidence": 0.72, "confidence_type": "heuristic",
     "reason": "Nearby endpoints with similar orientation"}
  ]
}
```

### `road_events.json` — normalized provider events (example only)

```json
{
  "feed_mode": "example_not_live",
  "provider": "EXAMPLE_PROVIDER",
  "fetched_at": "2026-10-13T12:00:00+05:30",
  "events": [
    {
      "event_id": "example-001",
      "type": "road_closure",
      "status": "reported_closed",
      "geometry": {"type": "Point", "coordinates": [77.59, 12.97]},
      "reported_at": "2026-10-13T11:50:00+05:30",
      "last_updated_at": "2026-10-13T11:55:00+05:30",
      "source": "EXAMPLE_PROVIDER",
      "matched_edge_ids": [],
      "match_status": "unmatched",
      "match_confidence": null
    }
  ]
}
```

**Coordinates above are illustrative, not a verified closure.** GeoJSON point coordinates are `[longitude, latitude]` in WGS84. Never mix them with pixel coordinates. Provider status values should be mapped to our normalized schema with original raw status retained for audit.

### `analysis.json` (example)

```json
{
  "scenario": "reported_or_simulated_event",
  "affected_edge_ids": ["AB"],
  "route": {
    "source": "A", "target": "D", "reachable": true,
    "cost_before": 120, "cost_after": 185, "cost_unit": "pixels"
  },
  "newly_unreachable_destinations": 0
}
```

For imagery without reliable scale, use **pixels**, not kilometers or minutes. Dijkstra minimizes a chosen nonnegative edge cost; it does not establish road safety. For actual geographic distances, use valid georeferencing and suitable projection/geometry calculations.

## 8A. Topology repair and resilience-index specification

**Do not use `network fully connected?` as a mandatory repair loop.** The PDF's proposed connectivity feedback loop (p. 6) is a useful idea, but real road networks can have valid dead ends, divided carriageways, private access roads, and legitimately disconnected areas. Our stopping condition is **no remaining evidence-supported candidate link above the chosen threshold**, not 100% connectivity.

1. Skeletonize the predicted mask and identify endpoints, intersections and components.
2. Generate *candidate* missing links only between plausible endpoint pairs within a defined pixel/metre radius.
3. Compute evidence features: endpoint gap distance, tangent alignment, image probability along gap, possible crossing constraints, and optionally reference OSM alignment (with provenance).
4. Assign a **heuristic confidence score**; tune thresholds on validation data. Report false positive connections explicitly.
5. Use union-find / Disjoint Set to track components. If using MST, minimize candidate costs **subject to plausibility constraints**, not over every component indiscriminately.
6. Preserve observed versus inferred provenance in every edge. Allow users to exclude inferred links from routing.
7. Evaluate against synthetic occlusions over known roads, and compare with a no-repair baseline. Use geographically separated evaluation imagery where feasible.

### Define the Resilience Index before computing it

**Suggested prototype index:**

`R = reachable_essential_origin_destination_pairs_after / reachable_essential_origin_destination_pairs_before`

Both counts must use the **same designated origins and destinations**, edge directionality and road-weight rules; define what happens if the baseline count is zero (display N/A). R measures **relative essential connectivity under a specified failure scenario**, not safety or guaranteed real-world disaster resilience. Additionally report newly unreachable facilities and shortest-path detour ratio where routes remain reachable.

For gatekeepers, report node/edge betweenness **alongside** articulation-point/bridge flags and observed edge/node-removal impacts. High betweenness does not automatically mean a closure is the most consequential for hospitals.

### Optional DEM flood scenario — clearly illustrative

If time and appropriate data permit, intersect roads with an elevation raster and a **stated hypothetical water-level threshold**. Display this as **terrain-based scenario / not observed flooding**. DEM vertical accuracy, drainage, levees, bridges, underpasses, and hydrodynamics can make simplistic flood thresholds misleading. Do not equate a modelled flood-risk flag with a confirmed live road closure.

## 9. Live incident matching and status rules

1. Fetch data only from an authorized provider.
2. Parse, normalize, and deduplicate incidents using stable provider IDs where available.
3. Preserve source, incident type, update time, fetch time, and provider-reported status.
4. Map-match event coordinates or line geometry to nearby graph edges **in the same coordinate reference system**.
5. Check proximity, road name/direction, event geometry, and matching confidence where available.
6. **Only confidently matched, explicitly closed** edges should be removed from routing; ambiguous matches must be flagged for review, not auto-closed.
7. Restrictions and hazards can increase route cost only under a documented, justified policy; do not invent speed reductions.
8. When an event expires or is withdrawn, restore the edge only according to the provider's semantics; keep an audit trail.
9. Recompute affected routes and accessibility after a status change.
10. Display **unknown/unreported** for roads without coverage. Display **stale/unavailable** if the feed fails.

**Map alignment risk:** A graph extracted from a 512×512 unreferenced image cannot be reliably matched to latitude/longitude incidents. For live integration, use a georeferenced road graph (for example, suitably licensed OSM road geometry) as the reference, then overlay or align extracted roads. Document any mismatch between the AI-derived graph and the live-routing graph.

## 10. GitHub collaboration

Branches: `ml-road-extraction`, `graph-live-backend`, `dashboard`, and protected `main`.

```bash
git checkout -b graph-live-backend
git add .
git commit -m "Add normalized incident adapter"
git push -u origin graph-live-backend
```

Use pull requests; integrate at least every three days. Keep raw datasets, large model checkpoints, API keys, and credentials out of Git. Suggested `.gitignore`:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.env
*.pt
*.pth
data/raw/
data/processed/
outputs/
models/
```

Daily 10–15-minute stand-up: completed, next, blocked. Save a known-good demo dataset and a recorded event replay for resilience.

## 11. Evaluation and success criteria

| Module | Test / metric |
|---|---|
| Segmentation | IoU, precision, recall, F1 on geographically separated held-out tiles |
| Road reconstruction | True recovered links, false inferred links, link precision/recall, connectivity compared with no-repair baseline; test MST/union-find heuristic separately |
| Graph extraction | Junction accuracy, reachability, topology correctness |
| Criticality | Edge/node ablation, articulation points, bridges, newly unreachable destinations, detour increase, defined resilience index |
| Live feed | Actual coverage, fetch success rate, update lag, stale detection, API error handling |
| Event-to-road matching | Correct matches, incorrect matches, unmatched events on a labelled sample |
| Dynamic routing | Route recalculation on event changes, no-route handling, restoration behavior |
| Dashboard | Clear labels, timestamps, correct overlays, stable operation on 4 GB laptop |

**Demonstrate actual improvement:** Compare the system with/without road reconstruction, and with/without reported closure updates. Do not claim superiority over Google Maps or other platforms without a proper benchmark.

## 12. Final presentation sequence

1. Problem: satellite road gaps and disruptions affect network accessibility.
2. Original satellite imagery and predicted road mask.
3. Road graph and inferred links with uncertainty.
4. Critical roads and why they rank highly.
5. Current road-event feed: **provider name, last update, coverage, mode (LIVE or REPLAY)**.
6. Incoming closure matched to a road segment; show evidence or explain ambiguity.
7. Automatic rerouting and hospital/shelter accessibility change.
8. Simulate a second closure and compare outcomes.
9. Quantitative results, limitations, and next steps.

## 12A. Optional post-MVP enhancements (only after all core gates pass)

- **Optical + SAR:** benchmark a registered optical/SAR fusion model against the optical-only baseline; do not add this without genuinely paired labels/data.
- **Terrain/flood overlay:** clearly labelled hypothetical DEM-derived hazard scenarios; not a live flood detector.
- **Full-stack UI:** migrate from Streamlit to the pitch's Next.js + FastAPI architecture only if the core system is stable and there is a compelling performance or deployment need.
- **Real-time feed expansion:** add a second verified city/provider only after one provider and map-matching pipeline work end-to-end.

## 13. Definition of done

A teammate can clone the project, install documented dependencies, open a prepared study area, inspect road extraction and inferred links, view criticality, see **provider-attributed automatically refreshed events if a verified feed is available**, and reproduce a route update. The UI reliably distinguishes **live**, **recorded replay**, **simulated**, **inferred**, **stale**, and **unreported** data.

**If no verified real-time provider is accessible for the study area, the project cannot honestly claim real-time road-status coverage.** Report the limitation, show the functioning integration layer with recorded events, and seek an alternative provider or geography.
