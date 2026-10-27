from pathlib import Path
import os,sys,time,json,ast,traceback,contextlib,io
ROOT=Path(__file__).resolve().parents[1]
w=ROOT/'outputs/reproduction'
w.mkdir(parents=True,exist_ok=True)
os.environ['MPLBACKEND']='Agg'
os.environ.setdefault('CAPYMOA_JVM_ARGS','-Xmx2g -Xss4M')
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
kind,base_name=sys.argv[1:3]
tag=kind+'__'+base_name
out=w/'runs';out.mkdir(exist_ok=True)
started=time.monotonic();result={'case':kind,'regressor':base_name,'status':'running'}
def progress(it,total=None,**kwargs):
 last=time.monotonic()
 for i,item in enumerate(it):
  if time.monotonic()-last>25:
   print(json.dumps({'case':tag,'rows':i,'total':total,'seconds':round(time.monotonic()-started)}),flush=True);last=time.monotonic()
  yield item
try:
 import numpy as np
 import pandas as pd
 import matplotlib.pyplot as plt
 from collections import deque,defaultdict
 from math import sqrt
 from sklearn.preprocessing import OneHotEncoder
 from sklearn.metrics import mean_absolute_error,mean_squared_error
 import capymoa
 from capymoa.regressor import KNNRegressor,FIMTDD,AdaptiveRandomForestRegressor
 from capymoa.stream import Schema,NumpyStream
 from capymoa.instance import RegressionInstance
 r=ROOT
 notebook=json.loads((r/'notebooks/experiments.ipynb').read_text(encoding='utf8'))
 codes={i:''.join(c['source']) for i,c in enumerate(notebook['cells'][2:]) if c['cell_type']=='code'}
 selected={'KNN':KNNRegressor,'FIMTDD':FIMTDD,'ARF':AdaptiveRandomForestRegressor,'none':None}[base_name]
 ns={'np':np,'pd':pd,'plt':plt,'deque':deque,'defaultdict':defaultdict,'sqrt':sqrt,'tqdm':progress,'OneHotEncoder':OneHotEncoder,'mean_absolute_error':mean_absolute_error,'mean_squared_error':mean_squared_error,'Schema':Schema,'NumpyStream':NumpyStream,'RegressionInstance':RegressionInstance,'KNNRegressor':KNNRegressor,'FIMTDD':FIMTDD,'AdaptiveRandomForestRegressor':AdaptiveRandomForestRegressor,'base_regressor':FIMTDD,'base_regressors_to_test':[selected]}
 all_nodes=[n for code in codes.values() for n in ast.parse(code).body]
 definitions=[n for n in all_nodes if isinstance(n,ast.ClassDef) or isinstance(n,ast.FunctionDef) and n.name=='prequential_evaluation']
 exec(compile(ast.Module(body=definitions,type_ignores=[]),'<original definitions>','exec'),ns)
 os.chdir(r)
 print(json.dumps({'case':tag,'capymoa':capymoa.__version__,'phase':'started'}),flush=True)
 if kind=='per_stop_all':
  ns['selected_model']=ns['NaiveAllPerStopRegressor'];exec(compile(codes[11],'<original per-stop variant 1>','exec'),ns)
  mae,rmse=ns['mae'],ns['rmse']
 elif kind=='per_stop_single':
  ns['selected_model']=ns['NaivePerStopRegressor'];exec(compile(codes[17],'<original per-stop variant 2>','exec'),ns)
  mae,rmse=ns['mae'],ns['rmse']
 elif kind=='station_hour':
  nodes=ast.parse(codes[47]).body
  # Only select one of the original three calls; retain setup and function unchanged.
  nodes=[n for n in nodes if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='evaluate_model')]
  def capture_mae(a,b):
   value=mean_absolute_error(a,b);ns['_case_mae']=value;return value
  def capture_mse(a,b):
   value=mean_squared_error(a,b);ns['_case_mse']=value;return value
  ns['mean_absolute_error']=capture_mae;ns['mean_squared_error']=capture_mse
  exec(compile(ast.Module(body=nodes,type_ignores=[]),'<original station-hour code>','exec'),ns)
  ns['evaluate_model'](selected,base_name,ns['X_array'],ns['y_array'])
  mae,rmse=ns['_case_mae'],sqrt(ns['_case_mse'])
 else:
  models={'baseline':'SuperNaiveModel','combined':'NaiveRegressorChunked','integrated':'NaiveRegressorIntegrated','seasonal':'SeasonalRegressorIntegrated','time_context':'TimeRegressorIntegrated','exogenous':'ExogenousRegressorIntegrated'}
  df=pd.read_csv('data/processed/loader_f30avg.csv',index_col=0)
  context=pd.read_csv('data/processed/context_lagged.csv',index_col=0) if kind in ['seasonal','time_context','exogenous'] else None
  mae,rmse,maes,rmses=ns['prequential_evaluation'](ns[models[kind]],df,context_df=context,base_regressor=selected,plot=False)
  result['windowed_mae']=[float(v) for v in maes];result['windowed_rmse']=[float(v) for v in rmses]
 result.update(status='completed',mae=float(mae),rmse=float(rmse),capymoa=capymoa.__version__)
except BaseException as exc:
 result.update(status='failed',error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc());traceback.print_exc()
result['seconds']=round(time.monotonic()-started,3)
(out/(tag+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['windowed_mae','windowed_rmse','traceback']}),flush=True)
sys.exit(0 if result['status']=='completed' else 1)
