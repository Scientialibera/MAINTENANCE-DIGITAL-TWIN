# Architecture

```text
NASA C-MAPSS archive             NASA IMS bearing archive
        |                                  |
        v                                  v
ml/cmapss.py                     ml/bearing_features.py
        |                                  |
        +---------------+------------------+
                        |
                        v
             services/fleet_repository.py
                        |
              +---------+----------+
              |                    |
              v                    v
     QuantileForestRUL       Digital Twin Scenario
       RUL P10/P50/P90       load / heat / vibration
              |                    |
              +---------+----------+
                        |
                        v
                    FastAPI
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
   Plant UI        Asset Twin     Maintenance MILP
```

## Runtime data modes

The application has two explicit data modes.

`nasa-cmapss-fd001` loads the complete downloaded FD001 training file. Fleet rows are real C-MAPSS engine trajectories. If a trained model artifact exists, asset RUL is model output. If it does not, the benchmark training RUL is displayed and labelled as a benchmark label rather than a prediction.

`nasa-cmapss-excerpt` is the offline mode committed to the repository. It contains actual C-MAPSS FD001 rows for engine 1. The multi-asset layout uses deterministic demonstration states so the UI remains operational before the full 12 MB NASA archive is downloaded. Those states are labelled as scenario seeds and are not presented as measured plant assets.

## API boundaries

- `/api/fleet` returns current asset-level health and RUL state.
- `/api/assets/{asset_id}` returns telemetry history and maintenance cost assumptions.
- `/api/assets/{asset_id}/simulate` applies what-if operating conditions to the current state.
- `/api/model/status` and `/api/model/validation` expose model provenance and measured validation only when a trained artifact exists.
- `/api/maintenance/optimize` solves a resource-constrained maintenance scheduling problem.

## Deployment

There is intentionally no CI/CD configuration in this repository. The Dockerfile is a runtime packaging option only and does not create an automated deployment pipeline.
