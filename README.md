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

## 2. Revised team division: core engineering first, dashboard last

**The interactive dashboard is owned by the integration lead and begins in Week 6.** Until then, use CLI commands, notebooks, saved PNGs, GeoJSON/JSON files, and pytest for output. The three core modules are developed **in parallel**, using agreed fixtures.

| Owner | Primary work | Computing | Contract/deliverable |
|---|---|---|---|
| **You — graph, topology, integration, final dashboard** | Skeletonization, pixel/geospatial graph building, Dijkstra, topological gap validation, edge/node criticality, emergency accessibility, module integration; Streamlit in Week 6 | RTX 3050 laptop (CPU sufficient for graph tasks; GPU available for troubleshooting) | `road_graph.json`, `analysis.json`, reproducible CLI pipeline, final dashboard |
| **Teammate 1 — satellite AI/ML** | Dataset licensing/splits, preprocessing, lightweight U-Net, training, inference, segmentation evaluation, occlusion robustness experiments | Google Colab/Kaggle cloud GPU **if available**, otherwise your RTX 3050 for agreed training windows | `road_mask.png`, training/inference scripts, checkpoint metadata, IoU/F1 report |
| **Teammate 2 — live status and geospatial data** | Verify authorized incident provider and area coverage, normalize event records, geographic map matching, refresh/staleness handling, status overlays, event replay and API tests | Local CPU laptop (4 GB RAM is enough for API tests); cloud notebook optional | `road_events.json`, `matched_events.json`, feed adapter, provider feasibility report |

**Collaboration:** Teammate 1 must not wait for graph code; Teammate 2 must not wait for real ML output. You must not wait for either: begin with a small synthetic graph and a fixed mask. Share interface contracts on Day 1. The owner of the dashboard is **you**, not Teammate 2.

**Cloud notebook policy:** Keep the source of truth in GitHub, not in ephemeral Colab sessions. Mount data from an approved source, save checkpoints and predictions to durable storage, and record model version, dataset split, seed, and library versions. Never commit tokens or private datasets. Cloud GPU availability, quotas, and session lifetime are not guaranteed; keep a CPU or local-GPU fallback. Do not run heavy training on the 4 GB laptop.

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

## 4. Revised six-week schedule (42 days) — core first

### Week 1 — Agreements and feasibility (Days 1–7)

- **You:** Create repository, `schemas.py`, synthetic 10–20-node graph, Dijkstra CLI and edge-removal tests. Set exact coordinate and edge-ID conventions.
- **Teammate 1:** Choose a licensed road imagery dataset, inspect image/mask pairs, create geographically separated train/validation/test splits, set up cloud notebook and verify training device. Export one sample `road_mask.png`.
- **Teammate 2:** Test actual provider access for the chosen study area. Record endpoint, auth, quotas, coverage, incident geometry, timestamps, terms and a redacted sample response. Define normalized event schema.

**Gate:** Synthetic rerouting works; mask and event fixtures validate; live-provider go/no-go is documented. Do not postpone provider feasibility to Week 4.

### Week 2 — First working components (Days 8–14)

- **You:** Skeleton-to-graph conversion, junction/endpoints, graph connectivity, weighted Dijkstra and CLI output. Validate paths on small known masks.
- **Teammate 1:** Train lightweight U-Net baseline (e.g., 256×256 tiles; adjust batch to available VRAM), run inference, report IoU/F1 on held-out images.
- **Teammate 2:** Implement provider adapter, event normalization, polling client, deduplication and fixture-based tests. If live access is unavailable, retain replay as a **clearly labelled fallback**, not a live-data claim.

**Gate:** Image/mask → graph → shortest path in CLI; separately provider/fixture → normalized event JSON.

### Week 3 — Occlusion recovery and network criticality (Days 15–21)

- **You:** Candidate link geometry, endpoint direction and proximity checks; bridges, articulation points, betweenness, edge/node ablation and resilience-index definition. Reject unsupported links rather than forcing full connectivity.
- **Teammate 1:** Run controlled artificial-occlusion tests on known roads; compare no-repair vs reconstruction; measure false connections and correct recovered links. Coordinate inferred-link format with you.
- **Teammate 2:** Implement incident-to-edge matching on a **georeferenced** sample graph, match-distance thresholds, ambiguity handling, and test cases for unmatched incidents.

**Gate:** A tested missing-road scenario, graph criticality ranking, and one incident matched (or explicitly unmatched) to a known road segment.

### Week 4 — Dynamic status and backend integration (Days 22–28)

- **You:** Integrate segmentation outputs, reconstructed links and graph analytics. Build backend function that accepts affected edge IDs and recalculates routes, accessibility and criticality.
- **Teammate 1:** Finalize inference pipeline and metadata; run on the selected study area; assist with georeferencing only where valid. Freeze a reproducible baseline checkpoint.
- **Teammate 2:** Connect provider polling → normalized events → map matching → graph-status updates; implement timestamps, freshness, expiration, API errors and recorded replay.

**Gate:** One reproducible **headless** end-to-end run: prepared image → graph + status events → updated routing results, saved to JSON. No dashboard needed yet.

### Week 5 — Accuracy, reliability and complete core pipeline (Days 29–35)

- **You:** Integrate emergency destinations, rerouting, criticality stress tests, CLI entry point and automated end-to-end tests. Resolve edge-ID, CRS and coordinate mismatches.
- **Teammate 1:** Compare baselines, finalize held-out evaluation, document false positives and limitations. Export sample images/masks and lightweight inference artifacts.
- **Teammate 2:** Test real provider requests when available; validate map matching, deduplication, stale-feed behavior, event expiration and latency. Provide attributed replay fixtures for deterministic demo.

**Gate:** **Core-engine freeze by Day 35.** Command-line demo and evaluation must work independently of Streamlit. If provider coverage is missing, say so explicitly and demonstrate replay separately.

### Week 6 — Dashboard by you, documentation by teammates (Days 36–42)

- **You:** Build Streamlit + Plotly/Folium dashboard over stable backend APIs: imagery/mask/graph layers, inferred-link confidence, criticality ranking, provider attribution and freshness, simulated vs reported closures, before/after routes. Keep UI separate from model training and polling.
- **Teammate 1:** Package ML instructions, checkpoints, inference outputs, plots, methodology, and benchmark tables; support integration debugging.
- **Teammate 2:** Package provider setup, event samples, rate-limit/staleness documentation, integration tests and failure-mode evidence; support final demo.
- **Days 40–41:** Clean-install test, presentation rehearsal, feature freeze, screenshots and recorded fallback.
- **Day 42:** Final demonstration and tagged release.

**Critical fallback:** If the dashboard runs late, the Week 5 CLI demo remains valid. If training fails, use a clearly labelled reference mask; if live provider data is unavailable, label the incident demo **REPLAY**, not LIVE.

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

## 6A. Core-first deliverables and integration commands

Before the dashboard, each module must expose a deterministic callable Python function or CLI script:

1. **ML:** `image → road_mask.png` with inference metadata and held-out evaluation.
2. **Graph:** `road_mask.png + optional inferred_links.json → road_graph.json`; `road_graph.json + closures → analysis.json`.
3. **Live/geospatial:** `provider response → road_events.json → matched_events.json`, preserving source, timestamps, coordinate reference system and match confidence.
4. **Integration:** `graph + matched events + destination nodes → updated graph and before/after accessibility report`.

These are **interface targets**, not commands that already exist. Agree on names and arguments in `docs/decisions.md` before writing scripts. Test the interfaces using tiny sample fixtures and avoid copying notebooks manually between teammates.

**Minimum shared tests:** empty road mask; isolated node; disconnected components; ambiguous incident location; stale event; duplicate event; no closure events; invalid CRS; low-confidence inferred link; missing hospital node. Report pixel-distance results as pixels until georeferencing is validated.

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

---

## 14. Cloud notebook requirements and limits (read before starting)

**No dedicated local GPU is required to use Google Colab or Kaggle Notebooks.** Computation runs on remote machines. The teammate needs a working browser, account access, and a reliable internet connection. A 4 GB RAM laptop can use the browser, but large uploads, many browser tabs, or local image processing may still be slow. Free GPU access is **not guaranteed**: hardware, quotas, session length, and availability vary. The runtime's RAM, disk, and GPU are different from the laptop's. A cloud notebook is not permanent storage.

**ML lead's cloud setup:**

1. Sign into Google Colab at https://colab.research.google.com/ and create `notebooks/01_dataset.ipynb` (or a Kaggle notebook if Colab GPU is unavailable).
2. Choose **Runtime → Change runtime type → T4 GPU** or another available GPU. If the GPU option is missing, try a CPU preprocessing session and schedule GPU training later; do not assume free GPUs are always available.
3. In a code cell, run:

   ```python
   import torch
   print('PyTorch:', torch.__version__)
   print('CUDA available:', torch.cuda.is_available())
   if torch.cuda.is_available():
       print('GPU:', torch.cuda.get_device_name(0))
   ```

4. Clone the shared GitHub repository **inside the notebook runtime** (replace the URL):

   ```python
   !git clone https://github.com/YOUR-ORG/route-resilience.git
   %cd route-resilience
   !pip install -q numpy opencv-python-headless scikit-image pillow matplotlib pandas
   ```

5. Download datasets only from authorized, licensed sources. Save persistent datasets/checkpoints in Google Drive or another permitted durable location; use `/content/` only for temporary working copies. To mount Drive in Colab:

   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

6. Save a checkpoint at the end of every training epoch or sensible interval, plus a CSV of loss/metrics. Restarting a runtime may erase everything in its temporary disk.
7. Download/export final `road_mask.png`, the checkpoint, dataset split manifest, and metrics report. Push **source code and small fixtures** to GitHub, not raw datasets or large `.pth` files.
8. Keep inference runnable on CPU (slower is fine), so the final demo does not require an active Colab session.

**Graph lead (you):** NetworkX and scikit-image work on CPU; Colab is optional. Your RTX 3050 is a backup training resource, not a dependency for graph work.

**Live-data lead:** Cloud notebooks can test API parsing, but are poor choices for an always-on live poller because sessions disconnect. Build a restartable local Python command for fetching one snapshot; later the final dashboard can trigger controlled refreshes. Never put an API key directly in a shared notebook. Use environment variables or the notebook platform's secrets feature. Respect the provider's rate limits.

## 15. Detailed owner playbooks: what to build, in what order

### A. You — graph, topology, criticality, integration, final dashboard

**Week 1: synthetic graph first**

1. Create `src/graph/routing.py`. Make a 10–20 node NetworkX graph with positive edge lengths and implement `shortest_route(graph, source, target, excluded_edges=None)`.
2. Create `tests/test_routing.py` covering normal path, alternate path after removal, and disconnected source/target.
3. Write `data/samples/road_graph.json` conforming to Section 8. Confirm with both teammates that IDs, coordinates, CRS, edge units, and statuses are understood.
4. Print route path, path cost, and unreachable destinations to the terminal. No dashboard yet.

**Week 2: image mask to graph**

1. Implement `src/graph/build_graph.py`: threshold binary road mask, skeletonize, detect endpoints/junctions, trace segments, and construct nodes/edges.
2. Preserve polyline geometry and **pixel length**; avoid inventing meter distances for ungeoreferenced tiles.
3. Test a straight road, T-junction, loop, disconnected roads, and crossing that should/shouldn't connect.
4. Export a graph JSON plus a diagnostic PNG overlay for ML lead review.

**Week 3: reconstruction and criticality**

1. Implement `src/graph/topology.py` to generate plausible endpoint connections using gap distance, direction continuity, and nearby image evidence. Use MST/Disjoint Set only to manage candidates/components; **do not connect every component automatically**.
2. Label each accepted connection `inferred`, with a heuristic confidence and a reason. Keep observed roads unchanged.
3. Implement `src/graph/criticality.py`: connected components, bridges, edge/node removal tests, betweenness centrality, and before/after accessibility to chosen destinations.
4. Define and document a specific Resilience Index with its denominator and treatment of unreachable destinations. Compare scores with and without inferred links.

**Weeks 4–5: integration**

1. Agree with live-data lead on `matched_events.json` and edge-ID matching.
2. Apply only adequately matched, current, provider-reported closures to the relevant graph scenario; preserve baseline graph for comparison.
3. Recompute routes/criticality when incident state changes; distinguish actual provider reports from simulations.
4. Provide a single reproducible CLI entry point such as `python -m src.pipeline --image ... --events ...` **after implementing it**. Add integration tests for stale reports, no events, unmatched incidents, and unreachable hospitals.

**Week 6: dashboard, owned by you**

1. Implement `app/dashboard.py` in Streamlit after JSON/CLI outputs are stable.
2. Tabs: Imagery & Segmentation; Reconstructed Network; Criticality; Live/Reported Status; What-if Closures; Evaluation.
3. Show a legend: observed, inferred, reported closure, simulated closure, stale/unavailable. Show source and last-update time for every live event.
4. Make a reliable offline/replay demo mode, clearly labelled **replay**; test before presentation.

**Your acceptance checklist:** graph extraction works on at least one predicted mask; all graph algorithms pass tests; real feed changes trigger correct recomputation; dashboard is a consumer of stable outputs, not where algorithms are implemented.

### B. Teammate 1 — satellite ML and occlusion experiments (Colab GPU)

**Week 1: data and setup**

1. Find a legally reusable high-resolution road extraction dataset with image/mask labels; record source URL, license, image resolution, and geographic coverage in `data/README.md`.
2. Check that labels align with imagery and that roads are distinguishable at the chosen resolution.
3. Split by geography into train/validation/test areas where possible; record the split manifest to avoid leakage.
4. Create a Colab notebook that loads an image and mask, visualizes both, and reports dimensions and class balance.

**Week 2: U-Net baseline**

1. Implement dataset loader and consistent preprocessing for image and mask. Resize/crop to small tiles (e.g. 256×256) for 6 GB-class GPUs or variable Colab GPU capacity.
2. Train a small U-Net with a suitable road/background loss; log training/validation loss, IoU, precision, recall, and F1.
3. Save the best checkpoint to durable storage and generate `road_mask.png` on a **held-out** tile.
4. Supply the graph lead with an original image, predicted mask, reference mask, and prediction metadata. Agree on binary mask convention `0/255`.

**Week 3: occlusion robustness**

1. Build controlled experiments by masking known road segments with synthetic tree/shadow-like patches or occlusion masks.
2. Compare a baseline segmentation result against a reconstruction-assisted output using the same hidden ground truth.
3. Measure recovered true connections **and false positive connections**; save visual before/after examples.
4. Provide confidence evidence; if scores are heuristics, label them as heuristics rather than calibrated probabilities.

**Weeks 4–5: reliability and packaging**

1. Tune only after a baseline is reproducible; avoid switching to large transformer models unless time permits.
2. Implement `src/ml/predict.py` so the graph lead can run inference on a prepared tile; add CPU fallback.
3. Deliver model version, preprocessing parameters, split manifest, test metrics, inference instructions, and at least three example outputs.
4. Test on a fresh geographic tile not used in training.

**Week 6:** Help verify segmentation overlays, finalize ML results and failure-case analysis, and document how to reproduce inference. Do not take over dashboard implementation.

**ML acceptance checklist:** another teammate can run inference on a prepared image; predictions align spatially; reported IoU/F1 are from held-out data; checkpoints are backed up; road reconstruction gains are evaluated against ground truth.

### C. Teammate 2 — real road-status feed and geospatial matching

**Week 1: feasibility gate (highest priority)**

1. Choose a candidate study area jointly with the team; **do not assume Bengaluru has a suitable publicly accessible closure API**.
2. Investigate authorized road incident/closure providers or official data feeds. For each, document: coverage area, types of incidents, access method, license, pricing, rate limit, update frequency, event coordinates/geometry, and whether real closure events are returned.
3. Run a permitted sample request. Save a **sanitized** response without secrets or personal information. Record fetch time and provider event timestamp separately.
4. By Day 7 present a clear **go/no-go**: provider + supported area + evidence of usable data. If unavailable, select a supported city with team approval or implement an attributed replay mode; never claim replay is live.

**Week 2: normalized event adapter**

1. Implement `src/live/provider_client.py` with timeouts, response validation, retry/backoff, and configurable polling limits.
2. Convert provider-specific fields to `road_events.json`: stable ID, type, reported status, geometry, source, event timestamp, fetched timestamp, expiry (if known), and confidence/quality metadata.
3. Save a small fixture in `data/samples/` and add tests for empty results, malformed payloads, rate limits, and duplicate IDs.

**Week 3: incident-to-road matching**

1. Work with the graph lead to ensure **both** events and graph geometries use compatible CRS. A pixel-only graph cannot reliably match latitude/longitude incidents without georeferencing or an explicit map transformation.
2. Implement `src/live/map_match.py` to select candidate edges within a defined tolerance, considering event geometry, direction, and road identity where available.
3. Output `matched_events.json` with candidate edge IDs, match confidence, and an `unmatched` state. Do not automatically close an ambiguous edge.
4. Test with known point/line incidents, intersections, parallel roads, and out-of-area events.

**Week 4: automatic status update**

1. Implement a refreshable snapshot function (not an endless loop in a notebook). Track event creation/update times and last successful fetch.
2. Define rules for `reported_closed`, `reported_restricted`, `unknown`, `stale`, and `unmatched`.
3. Send only well-matched current closures to graph lead's scenario updater; do not treat absence of reports as proof that roads are open.
4. Create a clearly labelled historical/replayed fixture for demonstrations during API outages.

**Week 5: integration and verification**

1. Demonstrate: new provider event → normalized event → matched edge → graph closure → rerouting.
2. Test expired reports, changed provider status, feed outage, quota failure, and duplicate events.
3. Record measured polling interval and observed event latency; avoid promising instantaneous coverage.

**Week 6:** Help validate live event cards, timestamps, attribution, and status legend in the dashboard. Write provider limitations and reproducibility notes.

**Live-data acceptance checklist:** evidence of a permitted real feed for the chosen area or an honestly labelled replay; tests for matching and freshness; no secrets committed; current status never inferred solely from satellite imagery.

## 16. Shared weekly handoff and team leadership routine

| Checkpoint | You submit | ML teammate submits | Live-data teammate submits |
|---|---|---|---|
| End Week 1 | Synthetic graph + Dijkstra tests | Dataset license + image/mask notebook | Provider feasibility report + sample response |
| End Week 2 | Mask-to-graph JSON + overlay | Trained baseline + held-out prediction | Normalized event JSON + API tests |
| End Week 3 | Inferred links + criticality report | Occlusion experiment + error metrics | Map-matched event JSON + ambiguity tests |
| End Week 4 | Graph status updater + CLI | Improved/reproducible inference | Refresh/staleness handler + integration fixture |
| End Week 5 | Complete backend pipeline + integration tests | Model and evaluation package | Verified live/replay scenario + latency report |
| End Week 6 | Dashboard + presentation | ML report and visuals | Provider report and demo support |

**Daily check-in (10 minutes):** Each teammate reports one completed output, one next task, and one blocker. **Twice weekly:** run tests on `main` and review interfaces. **Weekly:** show an actual artifact (code, test, image, JSON, or report), not only verbal progress. Use GitHub Issues with owner, due date, and acceptance test. Keep the Day 7 provider decision visible to everyone.

**Team lead rule:** If the live-data provider cannot be validated by Day 7, do not quietly postpone the decision until Week 5. Re-scope the supported study area or explicitly separate live integration from the replay demonstration.
