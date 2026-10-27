# Retained Python source

`legacy/` contains the team's earlier standalone model variants and data-preparation script. These files support provenance and comparison with the consolidated notebook. Their model algorithms are preserved; historical paths and execution assumptions are documented in [reproduction notes](../docs/REPRODUCIBILITY.md).

Use `notebooks/experiments.ipynb` as the principal research entry point. The legacy modules are not a newly packaged library and should not be imported indiscriminately: several execute loading/evaluation code at module scope.
