# Maintenance Digital Twin

Manufacturing predictive-maintenance POC combining asset telemetry, remaining-useful-life prediction, operating what-if analysis and maintenance scheduling.

The application is intentionally built around two separate analytical questions:

1. What is the current degradation state and remaining useful life of each asset?
2. Given limited crews and production downtime, which assets should be maintained and when?

The frontend uses a light industrial SaaS design. It includes Plant Overview, Asset Twin, Failure Risk, Maintenance Planner and Model Validation views.

## Data

The primary benchmark is NASA C-MAPSS. The project also supports the NASA IMS bearing dataset for physical vibration degradation features.

- NASA C-MAPSS: https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data
- NASA IMS Bearings: https://data.nasa.gov/dataset/ims-bearings

C-MAPSS is simulator-generated run-to-failure data. IMS contains physical bearing experiments. The distinction is preserved throughout the application and documentation.

A small real FD001 excerpt is committed under `data/sample/` so the application can be inspected without a multi-megabyte data download. When the full C-MAPSS archive is present, the data repository automatically switches to full benchmark trajectories.

## Main capabilities

### Plant Overview

- Interactive two-line plant topology
- Asset health ranking
- RUL P10/P50/P90
- Risk prioritization
- C-MAPSS telemetry trends
- Clear source mode and model state

### Asset Twin

- Light-theme rotating-equipment visualization with sensor callouts
- Current telemetry
- RUL uncertainty interval
- Load, heat, vibration and bearing-degradation scenarios
- Scenario wear acceleration and projected health
- Explicit separation of measured benchmark state from what-if output

### Failure Risk

- Fleet-level health and RUL ranking
- Transparent operational risk indicator
- Direct asset navigation

The displayed risk percentage is a prioritization transform over RUL and uncertainty. It is not presented as a plant-calibrated probability of failure.

### Maintenance Planner

- Resource-constrained maintenance scheduling
- Crew-capacity constraints
- Variable maintenance duration
- Risk-weighted failure consequence
- Planned maintenance cost
- Production loss
- MILP solved with `scipy.optimize.milp`
- Before/after expected-value comparison

### Model Validation

- Whole-engine validation split to avoid trajectory leakage
- RMSE
- MAE
- NASA asymmetric score
- P10-P90 interval coverage
- No fabricated metrics when a trained artifact is absent

## Architecture

```text
NASA C-MAPSS / IMS
        |
        v
Data repository and feature engineering
        |
        +-------- RUL model --------+
        |                           |
        +-------- Twin scenario ----+
                                    |
                                    v
                                  API
                                    |
           +------------------------+------------------------+
           |                        |                        |
           v                        v                        v
      Plant console             Asset twin           Maintenance MILP
```

See `docs/architecture.md` for component boundaries.

## Install and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn api.main:app --reload --port 8000
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn api.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000
```

## Download the full NASA data

```bash
python scripts/fetch_nasa_data.py --cmapss
python scripts/fetch_nasa_data.py --ims
```

The full datasets are stored under `data/raw/` and are intentionally excluded from Git.

## Train the RUL model

```bash
python scripts/train_rul_model.py
```

The model uses C-MAPSS FD001, caps the training RUL target at 125 cycles and keeps complete engine trajectories together during validation. The saved artifact is written to:

```text
models/cmapss_fd001_rul.joblib
```

Restart the API after training. The Model Validation screen will then report measured holdout metrics.

## IMS bearing features

After downloading IMS data, point the extractor at one of the experiment directories:

```bash
python scripts/extract_ims_features.py data/raw/IMS/<experiment-directory>
```

The extractor computes vibration RMS, kurtosis, crest factor and spectral energy.

## Tests

```bash
pytest -q
python scripts/check_no_emoji.py
```

## Repository policy

There is no GitHub Actions workflow and no CI/CD automation in this repository. Docker is provided only as a runtime packaging option.

The project contains no emoji characters. `scripts/check_no_emoji.py` provides a local enforcement check.

## Research basis

The implementation is guided by NASA prognostics research and maintenance-scheduling literature rather than a generic predictive-maintenance dashboard. See `docs/research-basis.md` for the papers and the exact boundary between implemented methods and simplified POC assumptions.
