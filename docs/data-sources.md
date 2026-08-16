# Data sources

## NASA C-MAPSS Jet Engine Simulated Data

Canonical dataset:
https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data

Direct archive:
https://data.nasa.gov/docs/legacy/CMAPSSData.zip

C-MAPSS is a high-fidelity simulator-generated run-to-failure benchmark. It is not physical field telemetry. The benchmark contains multiple engine trajectories, three operating settings and 21 sensor channels. FD001 contains 100 training trajectories and 100 test trajectories under one operating condition and one HPC-degradation fault mode. FD002, FD003 and FD004 increase the number of operating conditions and/or fault modes.

The training trajectory RUL label is computed as:

```text
RUL(unit, cycle) = max_cycle(unit) - cycle
```

The project caps the training target at 125 cycles for the benchmark model, which reduces the influence of the long healthy plateau on regression.

The bundled `data/sample/cmapss_fd001_excerpt.csv` contains real FD001 values for engine 1. It exists only to make the application inspectable before the full NASA archive is downloaded.

## NASA IMS Bearings

Canonical dataset:
https://data.nasa.gov/dataset/ims-bearings

Direct archive:
https://data.nasa.gov/docs/legacy/IMS.zip

These are physical bearing experiments supplied by the Center for Intelligent Maintenance Systems at the University of Cincinnati. The project includes an extractor for vibration RMS, kurtosis, crest factor and spectral energy. The IMS dataset is used as the physical vibration-degradation reference while C-MAPSS remains the fleet-level RUL benchmark.

## Data acquisition

```bash
python scripts/fetch_nasa_data.py --cmapss
python scripts/fetch_nasa_data.py --ims
```

Downloaded archives are extracted under `data/raw/`, which is gitignored.
