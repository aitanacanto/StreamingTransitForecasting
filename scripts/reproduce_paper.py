from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,json,time
SCRIPTS=Path(__file__).resolve().parent
w=SCRIPTS.parent/'outputs/reproduction'
w.mkdir(parents=True,exist_ok=True)
import sys
python=Path(sys.executable)
expected={
 'baseline':{'none':('7.431','17.863')},
 'station_hour':{'KNN':('10.37','33.69'),'FIMTDD':('20.85','49.11'),'ARF':('14.95','32.78')},
 'per_stop_all':{'KNN':('6.336','14.702'),'FIMTDD':('12.316','33.171'),'ARF':('29.939','70.226')},
 'per_stop_single':{'KNN':('7.165','15.178'),'FIMTDD':('9.583','22.152'),'ARF':('28.091','66.420')},
 'combined':{'KNN':('10.908','28.973'),'FIMTDD':('8.287','21.071'),'ARF':('56.723','96.274')},
 'integrated':{'KNN':('7.663','17.177'),'FIMTDD':('6.855','14.892'),'ARF':('8.050','17.053')},
 'seasonal':{'KNN':('7.313','16.711'),'FIMTDD':('6.240','14.104'),'ARF':('8.126','17.510')},
 'time_context':{'KNN':('7.313','16.711'),'FIMTDD':('7.422','15.532'),'ARF':('8.336','17.410')},
 'exogenous':{'KNN':('7.347','16.642'),'FIMTDD':('13.028','22.146'),'ARF':('8.165','18.883')},
}
tasks=[('seasonal','FIMTDD'),('baseline','none')]+[(k,b) for k,bs in expected.items() for b in bs if (k,b) not in [('seasonal','FIMTDD'),('baseline','none')]]
out=w/'runs';out.mkdir(exist_ok=True)
(w/'expected-table2.json').write_text(json.dumps(expected,indent=2),encoding='utf8')
def execute(task):
 kind,reg=task;tag=kind+'__'+reg;p=out/(tag+'.json')
 if p.exists() and json.loads(p.read_text(encoding='utf8')).get('status')=='completed':return task,json.loads(p.read_text(encoding='utf8'))
 with (out/(tag+'.log')).open('wb') as log:
  code=subprocess.run([str(python),'-X','utf8',str(SCRIPTS/'_paper_case.py'),kind,reg],stdout=log,stderr=subprocess.STDOUT).returncode
 if p.exists():return task,json.loads(p.read_text(encoding='utf8'))
 return task,{'case':kind,'regressor':reg,'status':'failed','error':'Child exited without result','exit_code':code}
results=[];start=time.monotonic()
print('Starting complete Table 2 reproduction: 25 cases; two isolated processes at a time.',flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:
 futures=[pool.submit(execute,task) for task in tasks]
 for future in as_completed(futures):
  (kind,reg),result=future.result();ex=expected[kind][reg]
  result['paper_mae']=float(ex[0]);result['paper_rmse']=float(ex[1])
  if result['status']=='completed':
   result['matches_reported_rounding']=all(round(result[key],len(value.split('.')[1]))==float(value) for key,value in zip(['mae','rmse'],ex))
   result['mae_difference']=result['mae']-float(ex[0]);result['rmse_difference']=result['rmse']-float(ex[1])
  results.append(result)
  (w/'table2-results.json').write_text(json.dumps({'total':25,'finished':len(results),'elapsed_seconds':round(time.monotonic()-start),'results':results},ensure_ascii=False,indent=2),encoding='utf8')
  print(json.dumps({'finished':len(results),'total':25,**{k:v for k,v in result.items() if k not in ['windowed_mae','windowed_rmse','traceback']}}),flush=True)
print('All Table 2 cases attempted and results saved.',flush=True)
