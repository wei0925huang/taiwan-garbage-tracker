from pathlib import Path
from datetime import datetime, timezone
import csv, io, json, os, urllib.request
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'data'; OUT.mkdir(exist_ok=True)
SOURCES={
 'newtaipei-live.json':('https://data.ntpc.gov.tw/api/datasets/28ab4122-60e1-4065-98e5-abccb69aaca6/csv/file','csv','LIVE_GPS'),
 'taipei-schedule.json':('https://data.taipei/api/dataset/6bb3304b-4f46-4bb0-8cd1-60c66dcd1cae/resource/a6e90031-7ec4-4089-afb5-361a4efe7202/download','csv','SCHEDULE'),
 'taichung-live.json':('https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=c923ad20-2ec6-43b9-b3ab-54527e99f7bc','json','DYNAMIC_DATA')}
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'TaiwanGarbageTracker/0.2 (+GitHub Actions)','Accept':'application/json,text/csv,*/*'})
 with urllib.request.urlopen(req,timeout=45) as r:return r.read()
def text(b):
 for enc in ('utf-8-sig','utf-8','cp950','big5'):
  try:return b.decode(enc)
  except UnicodeDecodeError:pass
 return b.decode('utf-8','replace')
def pick(d,*keys):
 low={str(k).strip().lower():v for k,v in d.items()}
 for k in keys:
  if k.lower() in low:return low[k.lower()]
 return ''
def num(v):
 try:return float(str(v).strip())
 except:return None
def normalize(d,kind):
 if kind=='LIVE_GPS':
  return {'dataType':kind,'lineid':pick(d,'lineid'),'lineName':'','car':pick(d,'car'),'time':pick(d,'time'),'location':pick(d,'location'),'longitude':num(pick(d,'longitude')),'latitude':num(pick(d,'latitude')),'cityname':pick(d,'cityname'),'speed':None,'arrival':''}
 if kind=='DYNAMIC_DATA':
  return {'dataType':kind,'lineid':pick(d,'lineid'),'lineName':'','car':pick(d,'car'),'time':pick(d,'time'),'location':pick(d,'location'),'longitude':num(pick(d,'X','longitude')),'latitude':num(pick(d,'Y','latitude')),'cityname':'臺中市','speed':num(pick(d,'SpeedValue','speedvalue')),'arrival':''}
 return {'dataType':kind,'lineid':pick(d,'路線'),'lineName':pick(d,'路線'),'car':pick(d,'車號'),'time':pick(d,'抵達時間'),'arrival':pick(d,'抵達時間'),'departure':pick(d,'離開時間'),'location':pick(d,'地點'),'longitude':num(pick(d,'經度')),'latitude':num(pick(d,'緯度')),'cityname':pick(d,'行政區'),'speed':None,'village':pick(d,'里別'),'team':pick(d,'分隊'),'trip':pick(d,'車次')}
def parse_json(obj):
 while isinstance(obj,dict):
  for k in ('records','result','data','Data'):
   if isinstance(obj.get(k),list):return obj[k]
   if isinstance(obj.get(k),dict):obj=obj[k];break
  else:return [obj]
 return obj if isinstance(obj,list) else []
def write(name,url,fmt,kind):
 old=OUT/name; previous={}
 try:
  if old.exists():previous=json.loads(old.read_text('utf-8'))
 except:pass
 try:
  b=get(url)
  items=list(csv.DictReader(io.StringIO(text(b)))) if fmt=='csv' else parse_json(json.loads(text(b)))
  records=[normalize(x,kind) for x in items if isinstance(x,dict)]
  records=[x for x in records if x['latitude'] is not None and x['longitude'] is not None]
  payload={'meta':{'sourceUrl':url,'dataType':kind,'fetchedAt':datetime.now(timezone.utc).isoformat(),'count':len(records),'error':''},'records':records}
  old.write_text(json.dumps(payload,ensure_ascii=False,indent=2),'utf-8');print(name,len(records))
 except Exception as e:
  if previous:
   previous.setdefault('meta',{})['error']=f'{type(e).__name__}: {e}';previous['meta']['lastAttemptAt']=datetime.now(timezone.utc).isoformat();old.write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf-8')
  else:
   old.write_text(json.dumps({'meta':{'sourceUrl':url,'dataType':kind,'fetchedAt':'','count':0,'error':f'{type(e).__name__}: {e}'},'records':[]},ensure_ascii=False,indent=2),'utf-8')
  print(name,'ERROR',e)
for name,(url,fmt,kind) in SOURCES.items():write(name,url,fmt,kind)
