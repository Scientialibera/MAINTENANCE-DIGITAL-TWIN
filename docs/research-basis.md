# Research basis

## C-MAPSS degradation benchmark

Saxena, Goebel, Simon and Eklund, 2008, *Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation*.

NASA NTRS:
https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20090029214.pdf

The paper describes the degradation simulation used to generate the PHM 2008 challenge data. This project follows the benchmark structure: independent engine trajectories, operating settings, multivariate sensor observations and remaining-useful-life prediction.

## C-MAPSS benchmark methodology review

Ramasso and Saxena, 2014, *Review and Analysis of Algorithmic Approaches Developed for Prognostics on CMAPSS Dataset*.

NASA NTRS:
https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20150007677.pdf

The review emphasizes preprocessing, operating-condition treatment, health-state estimation, uncertainty and consistent prognostic performance evaluation. The repository therefore uses whole-engine validation splits and exposes explicit model metrics rather than random row-level validation.

## RUL uncertainty

Sankararaman and Goebel, 2013, *Remaining Useful Life Estimation in Prognosis: An Uncertainty Propagation Problem*.

NASA NTRS:
https://ntrs.nasa.gov/citations/20140010623

The application treats RUL as an interval rather than a single exact number. The benchmark model derives P10, P50 and P90 estimates from the distribution of individual random-forest tree predictions. This is a practical benchmark uncertainty representation, not a full uncertainty-propagation implementation of the paper.

## Physical bearing degradation

NASA Prognostics Center of Excellence, *IMS Bearings*.

Dataset:
https://data.nasa.gov/dataset/ims-bearings

The physical vibration experiments are used to support bearing-condition features such as RMS, kurtosis, crest factor and spectral energy. These signals are a better physical reference for vibration degradation than the simulator-generated C-MAPSS benchmark.

## Maintenance scheduling

Gustavsson et al., 2023, *Integrated maintenance and production scheduling for unrelated parallel machines with setup times*.

Springer:
https://link.springer.com/article/10.1007/s10696-023-09511-z

The paper formulates resource-constrained maintenance and production scheduling with MILP and includes a real manufacturing case study. The POC implements a smaller MILP: an asset may be maintained at most once, active jobs consume crew capacity and the objective trades planned maintenance and production loss against risk-weighted expected failure consequences.

Additional formulation reference:

García Márquez et al., 2015, *The scheduling of maintenance. A resource-constraints mixed integer linear programming model*.

DOI:
https://doi.org/10.1016/j.cie.2015.06.006

## Boundaries

The application is a research and product-development POC. It is not a certified engine-health system, safety system or production maintenance authority. C-MAPSS is simulated data. The what-if twin uses a reduced-order wear-acceleration layer and must be replaced or calibrated with component-specific physics and plant telemetry for operational use.
