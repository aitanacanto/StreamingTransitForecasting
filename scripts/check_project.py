"""Offline structural checks; no model loading, network access or training."""
from pathlib import Path
from urllib.parse import unquote
import ast
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
errors = []
notebooks = list((ROOT / "notebooks").rglob("*.ipynb"))
for path in notebooks:
    notebook = json.loads(path.read_text(encoding="utf8"))
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            try:
                ast.parse("".join(cell.get("source", [])))
            except SyntaxError as exc:
                errors.append(f"{path.relative_to(ROOT)} cell {index}: {exc}")
            if cell.get("outputs"):
                errors.append(f"Unexpected saved output: {path.name} cell {index}")
for path in (ROOT / "src").rglob("*.py"):
    ast.parse(path.read_text(encoding="utf8"))
for path in ROOT.rglob("*.md"):
    for match in re.findall(r'\]\(([^)]+)\)|(?:href|src)="([^"]+)"', path.read_text(encoding="utf8")):
        target = next(item for item in match if item)
        if not target.startswith(("http:", "https:", "#")):
            if not (path.parent / unquote(target.split("#")[0])).is_file():
                errors.append(f"Broken link in {path.relative_to(ROOT)}: {target}")
counts = {}
for path in (ROOT / "data").rglob("*.csv"):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        count = 0
        for row in reader:
            count += 1
            if len(row) != len(header):
                errors.append(f"CSV column mismatch: {path.relative_to(ROOT)} row {count+1}")
                break
        counts[str(path.relative_to(ROOT))] = count
        if count == 0:
            errors.append(f"Empty data table: {path.relative_to(ROOT)}")
with (ROOT / "docs/provenance.csv").open(encoding="utf8", newline="") as stream:
    for row in csv.DictReader(stream):
        path = ROOT / row["destination"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row["prepared_sha256"]:
            errors.append(f"Artifact differs from preparation manifest: {row['destination']}")
for path in ROOT.rglob("*"):
    if path.is_file() and (path.name in {"flu_dataset.csv", "salvador_dengue.csv"} or path.suffix in {".pkl", ".pickle"}):
        errors.append(f"Excluded source artifact present: {path.relative_to(ROOT)}")
if errors:
    print("CHECKS FAILED")
    print("\n".join(errors))
    raise SystemExit(1)
print(f"PASS: {len(notebooks)} notebooks, Python syntax, documentation links, {len(counts)} CSV tables and artifact hashes.")
print("No training, predictions, pickle loading or network calls were performed.")
print("This structural check does not rerun models; see docs/REPRODUCIBILITY.md for the completed scientific reproduction.")
