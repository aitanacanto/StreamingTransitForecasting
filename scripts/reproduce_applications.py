from pathlib import Path
import os,sys,json,ast,time,traceback
ROOT=Path(__file__).resolve().parents[1]
w=ROOT/'outputs/reproduction'
w.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('CAPYMOA_JVM_ARGS','-Xmx2g -Xss4M')
os.environ['MPLBACKEND']='Agg'
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
mode=sys.argv[1]
out=w/'applications';out.mkdir(exist_ok=True)
started=time.monotonic();result={'application':mode,'status':'running'}
def progress(it,total=None,**kwargs):
 last=time.monotonic()
 for i,item in enumerate(it):
  if time.monotonic()-last>25:
   print(json.dumps({'application':mode,'phase_rows':i,'total':total,'seconds':round(time.monotonic()-started)}),flush=True);last=time.monotonic()
  yield item
try:
 import numpy as np,pandas as pd,matplotlib.pyplot as plt
 from matplotlib.animation import FuncAnimation,PillowWriter
 from collections import deque,defaultdict
 from math import sqrt
 import capymoa
 from capymoa.regressor import KNNRegressor,FIMTDD,AdaptiveRandomForestRegressor
 from capymoa.stream import Schema,NumpyStream
 from capymoa.instance import RegressionInstance
 r=ROOT
 nb=json.loads((r/'notebooks/experiments.ipynb').read_text(encoding='utf8'))
 codes={i:''.join(c['source']) for i,c in enumerate(nb['cells'][2:]) if c['cell_type']=='code'}
 ns={k:v for k,v in locals().copy().items() if k in ['np','pd','plt','FuncAnimation','PillowWriter','deque','defaultdict','sqrt','Schema','NumpyStream','RegressionInstance','KNNRegressor','FIMTDD','AdaptiveRandomForestRegressor']}
 ns.update(base_regressor=FIMTDD,tqdm=progress)
 nodes=[n for code in codes.values() for n in ast.parse(code).body]
 defs=[n for n in nodes if isinstance(n,ast.ClassDef) or isinstance(n,ast.FunctionDef) and n.name=='prequential_evaluation']
 exec(compile(ast.Module(body=defs,type_ignores=[]),'<retained definitions>','exec'),ns)
 os.chdir(r)
 ns['df']=pd.read_csv('data/processed/loader_f30avg.csv',index_col=0);ns['df'].index=pd.to_datetime(ns['df'].index)
 ns['df_contextual_data']=pd.read_csv('data/processed/context_lagged.csv',index_col=0);ns['df_contextual_data'].index=pd.to_datetime(ns['df_contextual_data'].index)
 if mode=='recommendation':
  # Path setup only: the retained cell asks for BusStops.csv in MoreModels,
  # while that same dataset lives in the sibling station_recommendation_system.
  setup=codes[69]
  for index in [69,70,71,72,73,74,75,76,77,78,79,80]:
   exec(compile(setup if index==69 else codes[index],'<original application cell '+str(index)+'>','exec'),ns)
  rows=[]
  for timestamp,value in ns['simulation_results'].items():
   for stop,rec in value['busy_stations'].items():rows.append({'timestamp':str(timestamp),'busy_stop':stop,'alternative_stop':rec['station'],'distance':float(rec['distance']),'score':float(rec['score'])})
  pd.DataFrame(rows).to_csv(out/'recommendations.csv',index=False)
  chosen=[row for row in rows if row['timestamp'][11:16] in ['17:15','17:20','17:25'] and row['timestamp'].startswith('2024-04-11')]
  result.update(status='completed',timestamps=len(ns['simulation_results']),recommendations=len(rows),paper_example_times=chosen)
  for index in [81,83]:exec(compile(codes[index],'<original animation definition>','exec'),ns)
  ns['save_busyness_animation_gif'](ns['station_coordinates'],ns['simulation_results'],ns['example_time_range'],filename=str(out/'reproduced-station-busyness.gif'))
  result['animation_generated']=True
 elif mode=='feature_importance':
  values=ns['prequential_evaluation'](ns['ExogenousRegressorIntegrated'],ns['df'],context_df=ns['df_contextual_data'],base_regressor=AdaptiveRandomForestRegressor,plot=False,return_model=True)
  mae,rmse,maes,rmses,model=values
  ns['exogenous_models']={'AdaptiveRandomForestRegressor':{'model':model}}
  result.update(training_mae=float(mae),training_rmse=float(rmse),training_samples=len(model.log))
  (out/'feature_importance-training.json').write_text(json.dumps(result,indent=2),encoding='utf8')
  for index in [49,50,51,53]:exec(compile(codes[index],'<original attribution cell '+str(index)+'>','exec'),ns)
  ns['mean_importance'].to_csv(out/'feature-importances.csv',header=['mean_absolute_importance'])
  result.update(status='completed',rows_explained=len(ns['explanations_df']),features=len(ns['mean_importance']),importances={str(k):float(v) for k,v in ns['mean_importance'].items()})
 else:raise ValueError(mode)
except BaseException as exc:
 result.update(status='failed',error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc());traceback.print_exc()
result['seconds']=round(time.monotonic()-started,3)
(out/(mode+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='traceback'},ensure_ascii=False),flush=True)
sys.exit(0 if result['status']=='completed' else 1)
