# Reproduction results

The experiments were executed with the retained notebook algorithms, CapyMOA **0.8.2**, Python **3.12** and Java **17.0.17**, using all **218,400 stop/time rows**. Paths were adapted to the repository layout; model logic, evaluation order and default model parameters were preserved.

| Paper result | Reproduction |
| --- | --- |
| Table 2 · model comparison | **25/25 combinations; 50/50 MAE/RMSE values match the published precision.** |
| Best model · seasonal FIMT-DD | MAE **6.240388**, RMSE **14.104050**, matching **6.240 / 14.104** in the paper. |
| Table 3 · station recommendations | **All six examples and rounded distances reproduced**, on 5 April 2024. |
| Table 4 · feature importances | **All 20 displayed values match to six decimal places**, after explaining 218,396 instances across 35 features. |
| Data | Ten stops, 21,840 timestamps, 1 March–31 May 2024. Targets match the retained daily-boundary preprocessing. |

Detailed outputs: [model comparison](results/table2-reproduction.csv), [recommendation examples](results/table3-recommendations.csv), [feature importances](results/feature-importances.csv) and [validation summary](results/validation-summary.json). The computed attribution also contains a small PM2.5 value, approximately 0.000019, which is absent from the paper's displayed table.

## Repeat the checks

Install the tested scientific environment using the [setup guide](SETUP.md), then run:

```sh
python scripts/check_project.py
python scripts/check_baseline.py
python scripts/reproduce_paper.py
python scripts/reproduce_applications.py recommendation
python scripts/reproduce_applications.py feature_importance
```

The full model comparison runs two isolated processes at a time and reuses completed case outputs. Generated logs, metrics and animation go to `outputs/reproduction/`. Full reproduction can take around an hour or longer, depending on hardware. `requirements-validation.txt` records the exact tested scientific packages; it does not assert recovery of the historical environment.

## Evaluation limitations

Numerical agreement confirms correspondence with the paper's reported results; it does not independently validate the evaluation design.

- The station/hour baseline trains on instances before later evaluating them, and its delay queue mixes stops.
- Shared-model buffers can expose a future label to another stop at the same timestamp. Lag windows also receive repeated observations when several rows share a timestamp. These behaviors were confirmed with controlled execution of the original definitions.
- The target horizon shortens at the end of each operating day. Recommendation distances are approximations and assume compatible routes and feasible walking.
- The notebook contains exploratory and earlier prototype sections with shared-state dependencies. The supplied runners isolate the published experiments; successful reproduction does not mean that an uninterrupted “Run All” is supported through every historical section.

No model or evaluation algorithm was corrected to force agreement. Original research figures remain labelled as original project outputs.
