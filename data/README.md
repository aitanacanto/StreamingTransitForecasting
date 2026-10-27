# Data sources and prepared files

The included transport tables describe aggregate bus-stop activity, not individual passenger journeys. The repository contains selected local copies used by the team, not the full SUNT dataset.

| Folder or file | Content | Provenance |
| --- | --- | --- |
| `raw/5min/` | Boarding, alighting and estimated occupancy at ten stops, March–May 2024. | Retained team copies derived from SUNT. |
| `raw/30min/` | Thirty-minute versions used by earlier recommendation prototypes. | Retained team copies derived from SUNT. |
| `processed/loader_f30avg.csv` | Long-format observations and future-average target, one row per stop/time. | Copied from `MoreModels/loader_f30avg_new.csv`. |
| `processed/loader_f30avg_wide.csv` | Earlier wide-format target table used in early notebook sections. | Copied from `MoreModels/loader_f30avg_old.csv`. |
| `processed/context_lagged.csv` | Context features including cyclical time, weather, events and daily health counts. | Retained team feature table; hourly/daily lags are described in the paper. |
| `processed/context_not_lagged.csv` | Unlagged context used by historical exploratory analysis. | Not suitable as a substitute for lagged forecast inputs. |
| `reference/bus_stops.csv` | Stop identifiers, public stop names and coordinates. | Team copy of SUNT/GTFS stop metadata. |

## Attribution

**Salvador Urban Network Transportation (SUNT)**, version 1, 28 April 2025. DOI: [10.17632/85fdtx3kr5.1](https://data.mendeley.com/datasets/85fdtx3kr5/1). The source dataset record identifies **CC BY 4.0**. Credit the dataset creators and link the source record when redistributing its derived tables. Project-specific selection, aggregation, reshaping and target construction were performed by the student team; no new transformations were applied to the copied CSV files in this preparation.

Source repository: https://github.com/LabIA-UFBA/SUNT

The team's context features cite OpenDataSUS, Open-Meteo, Yahoo Finance and Google Trends. These providers have separate terms; the SUNT license does not cover them automatically. Feature collection and source references are described in the paper and historical exploration notebook.

## Excluded source records

`flu_dataset.csv` and `salvador_dengue.csv` are intentionally absent. They contain original health-record tables that are unnecessary for inspecting the forecasting experiments; the prepared context tables retain only aggregate features already used by the team. The historical exploration notebook contains references to these files but cannot run its health-data sections without separately obtaining them.

## Time-series evaluation

The intended target is the mean load of the following six five-minute observations. Daily-period boundary handling in the historical preprocessing script can shorten that horizon at the end of the day. Future targets are unavailable at prediction time. Verify per-stop label delays, chronological ordering and the use of lagged context before comparing any newly generated metrics with the paper. See [known issues](../docs/REPRODUCIBILITY.md).
