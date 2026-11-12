import math,random,json
from sqlalchemy import select,func
from src.config.database import Base,engine,Session
from src.models import User,CurveDataset,AlignmentPolicy,ShapeStudy,ShapeRun,ClusterReview,Report
from src.services.analysis import analyze
from src.utils.security import hash_password
from src.utils.time import now
from src.utils.serialization import serialize
from src.config.migrations import apply_compat_migrations

def seed():
 apply_compat_migrations(engine)
 with Session() as db:
  for role in ('admin','analyst','viewer'):
   if not db.get(User,role):db.add(User(id=role,email=role+'@tanyuan.demo',password=hash_password('Curve2026!'),role=role))
  rng=random.Random(2403);times=[float(i*2) for i in range(64)];curves=[]
  for k in range(48):
   group=k//12;shift=(k%4-1.5)*2;amplitude=72+group*5+(k%3)*2;center=[42,64,48,56][group]+shift;slope=[.12,.09,.18,.105][group]
   values=[amplitude/(1+math.exp(-slope*(t-center)))+8+math.sin(t/12)*.35+rng.gauss(0,.2) for t in times]
   if group==3:values[22+k%5]+=18
   curves.append({'curve_id':f'TY-{k+1:02}','label':f'模拟配方{group+1}·养护件{k+1:02}','values':[round(v,6) for v in values]})
  if not db.get(CurveDataset,'demo-data'):db.add(CurveDataset(id='demo-data',name='滩原·48条固化养护曲线',source='tanyuan_cure_20261112.json',times=times,curves=curves,created_at=now()));db.flush()
  for id,name,mode,w,t in [('demo-policy','每曲线标准化·窗口6·阈值0.16','zscore',6,.16),('demo-raw','原始量级·窗口6·阈值4','raw',6,4)]:
   if not db.get(AlignmentPolicy,id):db.add(AlignmentPolicy(id=id,name=name,normalization=mode,window=w,threshold=t,created_at=now()))
  db.flush()
  if not db.get(ShapeStudy,'demo-study'):
   snapshot={'dataset':serialize(db.get(CurveDataset,'demo-data')),'policy':serialize(db.get(AlignmentPolicy,'demo-policy'))}
   db.add(ShapeStudy(id='demo-study',name='48件养护样·形态归并初审',dataset_id='demo-data',policy_id='demo-policy',snapshot=snapshot,created_at=now()))
  db.flush()
  if not db.get(ShapeRun,'demo-run'):db.add(ShapeRun(id='demo-run',study_id='demo-study',status='completed',result=analyze(db.get(ShapeStudy,'demo-study').snapshot),error='',created_at=now()));db.flush()
  if not db.get(ClusterReview,'demo-review'):
   clusters=db.get(ShapeRun,'demo-run').result['tree']['clusters'];names=[{'cluster_id':c['cluster_id'],'name':('缓升固化' if i==0 else '延迟上升' if i==1 else '尖峰待核' if i==2 else '曲线族')+'·'+c['cluster_id']} for i,c in enumerate(clusters)]
   db.add(ClusterReview(id='demo-review',run_id='demo-run',version=1,base_version=0,names=names,note='以完整路径、距离矩阵和complete-link树复核；形态簇不是强度或质量等级，尖峰与时移需回到模拟原始读数解释。',decision='accepted',author='analyst@tanyuan.demo',created_at=now()));db.flush()
  if not db.get(Report,'demo-report'):
   run=db.get(ShapeRun,'demo-run');review=db.get(ClusterReview,'demo-review');title='滩原养护样·形态归并复核稿'
   db.add(Report(id='demo-report',run_id='demo-run',review_id='demo-review',review_version=review.version,title=title,snapshot={'run_id':run.id,'checksum':run.result['checksum'],'review_id':review.id,'review_version':review.version,'title':title,'names':review.names,'clusters':run.result['tree']['clusters'],'policy':run.result['policy']},published_by='admin@tanyuan.demo',created_at=now()))
  db.commit();return {m.__tablename__:db.scalar(select(func.count()).select_from(m)) for m in (User,CurveDataset,AlignmentPolicy,ShapeStudy,ShapeRun,ClusterReview,Report)}
if __name__=='__main__':print(json.dumps(seed(),ensure_ascii=False))
