# Local setup

The scientific reproduction was verified on Windows with **Python 3.12**, **CapyMOA 0.8.2**, **Temurin Java 17.0.17** and CPU-only PyTorch. Use a separate environment and a compatible 64-bit Java runtime. See the [CapyMOA setup guide](https://capymoa.org/setup/index.html) for Java discovery and `JAVA_HOME`.

## Install

Windows PowerShell, from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-validation.txt
```

Linux/macOS activation:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-validation.txt
```

The pinned scientific packages were tested on Windows; other platforms may need compatible wheel versions. CPU PyTorch wheels use the official PyTorch index listed in the requirements file. CapyMOA 0.8.2 imports PyTorch even though its package metadata does not declare that dependency.

Confirm the runtime:

```sh
java -version
python -c "import capymoa; print(capymoa.__version__)"
```

## Reproduce the paper

```sh
python scripts/check_project.py
python scripts/check_baseline.py
python scripts/reproduce_paper.py
```

The first command checks file structure and integrity. The second rechecks the simple mean baseline. The full runner executes all 25 model combinations and writes results and logs to `outputs/reproduction/`; previously completed cases are reused. On the validation machine the model comparison took about 58 minutes. See [reproduction results](REPRODUCIBILITY.md).

Optional application checks:

```sh
python scripts/reproduce_applications.py recommendation
python scripts/reproduce_applications.py feature_importance
```

The recommendation check also regenerates the animation. Feature attribution evaluates every retained logged instance and can take tens of minutes.

## Open notebooks

To add the notebook interface:

```sh
python -m pip install -r requirements.txt
python -m jupyterlab
```

Open `notebooks/experiments.ipynb`, select this environment's Python kernel and run its initial path-setup cell. Later sections depend on earlier state; use the experiment runners for the isolated published comparisons. JupyterLab is an optional UI dependency, separate from the tested scientific lockfile.

`notebooks/archive/` and `src/legacy/` preserve earlier experiments. They may retain historical path assumptions or unfinished branches. Original health-record files are excluded; the principal experiments use the included aggregate context tables.
