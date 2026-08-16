# Product UI specification

The frontend follows a light industrial SaaS design system. This document is the implementation contract for the product-design step.

## Visual system

- Off-white application background
- White content cards
- Steel-grey typography and borders
- Muted blue for primary actions and prognostics
- Teal for healthy asset states
- Amber for maintenance attention
- Red reserved for critical asset risk
- No dark theme
- No gradients
- No marketing taglines
- No decorative chatbot
- No emoji characters

## Screen 1: Plant Overview

The left navigation contains Plant Overview, Asset Twin, Failure Risk, Maintenance Planner and Model Validation. The header contains the current page name, selected asset and API state.

Five KPI cards show asset availability, OEE proxy, critical assets, predicted failures and maintenance backlog. The main panel renders an interactive two-line plant topology with eight rotating-equipment assets. Each asset shows a health ring and RUL. A right-hand ranking panel orders assets by remaining life. A bottom chart plots C-MAPSS S2, S4 and S15 signals for the selected asset.

## Screen 2: Asset Twin

The main panel contains a simplified cutaway rotating-equipment/turbofan drawing with sensor callouts. Current C-MAPSS telemetry is shown beneath the equipment. RUL is rendered as P10, P50 and P90. A what-if panel controls load multiplier, ambient-temperature delta, vibration multiplier and bearing-degradation severity.

Scenario outputs must remain visually and semantically separated from measured benchmark telemetry.

## Screen 3: Maintenance Planner

The planner contains crew count, horizon and risk-tolerance inputs. The schedule is rendered as a weekly Gantt. Before/after cards show expected failure exposure, maintenance cost, production loss, failure cost avoided and net expected value.

The schedule comes from an explicit mixed-integer optimization model. The UI does not generate maintenance dates with rules or language-model text.
