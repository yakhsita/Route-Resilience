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

## Commands 

.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt        # NOTE: install when the venv is activated
python src/graph/<file_name.py>
python -m src.graph.<file_name_consisting_other_file_module>
python -m pytest tests/ -v
