## Directory Structure

```
Route-Resilience/
│
├── data/
│   └── raw/
│       └── koramangala_roads.graphml  # OSM road network from teammate
│
├── src/
│   └── graph/
│       ├── routing.py                 # Dijkstra
│       ├── road_closure.py            # Road closure simulation
│       ├── criticality.py             # Bridges and centrality
│       ├── resilience.py              # Connectivity resilience
│       ├── vulnerability.py           # Road vulnerability ranking
│       ├── multi_failure.py           # Multiple-road failures
│       ├── graph_io.py                # JSON graph import/export
│       ├── integration.py             # Combined graph analysis
│       └── osm_adapter.py             # NEW: OSM integration
│
├── tests/
├── outputs/
└── requirements.txt
```
## Graph integration
```
koramangala_roads.graphml
          |
          v
   OSM MultiDiGraph
          |
          +---------------------------+
          |                           |
          v                           v
 Directed routing graph       Undirected structural graph
          |                           |
          v                           v
  Custom Dijkstra              Bridge detection
  Vehicle rerouting            Articulation points
  Directed closures            Connectivity resilience
          |                           |
          +-------------+-------------+
                        |
                        v
            Route Resilience results
```
## Commands 

bash
```
python -m venv .venv 
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt        # NOTE: install when the venv is activated
python src/graph/<file_name.py>
python -m src.graph.<file_name_consisting_other_file_module>
python -m pytest tests/ -v
python -m pip freeze > requirements.txt      # to save all the requirements (in venv.) in the requirements.txt file 
```
## FILE STUCTURE & FUNCTION
```
          Route-Resilience/
          data/           # All input datasets and generated outputs
          raw/koramangala_roads.graphml — ✓ Actual directed OSM road network
          processed/koramangala_criticality.json — ✓ Day 11/13 analysis results
          processed/koramangala_impact_heatmaps.png — ✓ Day 13 heatmaps
          processed/*.geojson — NEW map layers for the frontend
          
          src/graph/ — ✓ Existing graph engine
          routing.py          # Custom Dijkstra shortest-path algorithm
          road_closure.py     # Single road closures on simple graphs
          criticality.py      # Bridges, articulation points, betweenness
          resilience.py       # Connectivity and failure resilience
          vulnerability.py    # Road-impact evaluation and ranking
          multi_failure.py    # Multiple simultaneous failures on simple graphs
          graph_io.py         # Graph validation and JSON import/export
          integration.py      # Combines graph analysis operations
          osm_adapter.py      # Loads OSM graph and matches GPS coordinates
          directed_closure.py # Closes directed OSM edges, preserving other directions
          real_road_simulation.py   # Day 9 real-map single closure
          real_multi_closure.py     # Day 10 cumulative multiple closures
          real_criticality.py       # Day 11/13 sampled criticality ranking
          criticality_heatmap.py    # Day 12 first rank-based heatmap
          impact_heatmaps.py        # Day 13 measured-impact heatmaps
          
          src/api/ — NEW FastAPI backend
          main.py — Starts FastAPI, registers routes
          routes/routing.py — Start/destination and shortest-path endpoints
          routes/closures.py — Simulate and manage road closures
          routes/analysis.py — Criticality results and statistics
          schemas.py — Validates request and response JSON
          services.py — Calls our existing graph algorithms
          
          src/dashboard/ — NEW Streamlit frontend
          app.py — Main dashboard entry point
          map_view.py — Folium/Leaflet map and map interactions
          api_client.py — Sends HTTP requests to FastAPI
          components.py — Metrics, controls and result panels
          pages/ — Criticality, closures, accessibility views
          
          src/database/ — NEW persistence
          models.py — Database tables
          db.py — Database connection
          repository.py — Save/load scenarios and reports
          src/ml/ and src/hazards/ — NEW integration modules
          Connect the U-Net road masks, reconstructed-road graphs, flood exposure layers, and other validated hazard datasets later.
          
          tests/ — ✓ Existing tests + NEW API/dashboard tests
          Keeps our graph regression tests and adds tests for REST endpoints, GeoJSON, closure sessions and mobile-compatible interactions.
          
          Project configuration
          requirements.txt — Python dependencies
          .env.example — NEW environment configuration without secrets
          README.md — Setup, run and testing instructions
          Dockerfile — NEW deployment packaging, later
```
