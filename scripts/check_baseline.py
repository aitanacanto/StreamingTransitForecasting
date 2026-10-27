"""Reproduce the retained notebook's mean baseline without importing CapyMOA."""
from pathlib import Path
import ast
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
notebook = json.loads((ROOT / 'notebooks/experiments.ipynb').read_text(encoding='utf8'))
definitions = []
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        for node in ast.parse(''.join(cell.get('source', []))).body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in {'SuperNaiveModel', 'prequential_evaluation'}:
                definitions.append(node)
if len(definitions) != 2:
    raise SystemExit('Expected baseline definitions not found in the notebook.')

# FIMTDD is an unused default argument for this mean-only baseline.
# Execute only the two selected definitions, not other notebook cells or imports.
scope = {'np': np, 'pd': pd, 'FIMTDD': object, 'tqdm': lambda iterable, **kwargs: iterable}
exec(compile(ast.Module(body=definitions, type_ignores=[]), '<notebook baseline>', 'exec'), scope)
data = pd.read_csv(ROOT / 'data/processed/loader_f30avg.csv', index_col=0)
mae, rmse, *_ = scope['prequential_evaluation'](scope['SuperNaiveModel'], data, plot=False)
matches = bool(round(float(mae), 3) == 7.431 and round(float(rmse), 3) == 17.863)
print(f'MAE: {mae:.6f}; RMSE: {rmse:.6f}')
print('Matches paper Table 2 to three decimal places.' if matches else 'Does not match paper Table 2 to three decimal places.')
raise SystemExit(0 if matches else 1)
