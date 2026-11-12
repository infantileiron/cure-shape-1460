import uuid
from fastapi import HTTPException
from sqlalchemy import select,func
from sqlalchemy.exc import IntegrityError
from src.models import ClusterReview,ShapeRun
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def _current_version(db,run_id):return db.scalar(select(func.max(ClusterReview.version)).where(ClusterReview.run_id==run_id)) or 0

def _conflict(base,current):
 return HTTPException(409,detail={'code':'review_version_conflict','message':f'复核版本冲突：本页基于 v{base}，当前最新为 v{current}；已拒绝保存，填写内容请保留后核对最新版本再提交','base_version':base,'current_version':current})

def _validate_names(run,names):
 expected={c['cluster_id'] for c in run.result['tree']['clusters']}
 if len(names)!=len(expected) or {n.get('cluster_id') for n in names}!=expected or any(set(n)!={'cluster_id','name'} or not n['name'].strip() or len(n['name'])>80 for n in names):
  raise HTTPException(422,'请为每个当前簇填写唯一对应的人工名称，保留完整簇ID')

def create(db,payload,user):
 run=require_completed(db,payload.run_id)
 _validate_names(run,payload.names)
 # Claim the run row before reading the baseline. PostgreSQL serialises review writers per
 # run; SQLite (local checks only) ignores this lock, so the unique constraint and retry loop
 # below remain the fallback invariant.
 db.execute(select(ShapeRun.id).where(ShapeRun.id==run.id).with_for_update())
 for attempt in range(3):
  current=_current_version(db,payload.run_id)
  if payload.base_version!=current:raise _conflict(payload.base_version,current)
  item=ClusterReview(id=str(uuid.uuid4()),version=current+1,created_at=now(),author=user['email'],**payload.model_dump());db.add(item)
  try:
   db.commit();return serialize(item)
  except IntegrityError:
   db.rollback()
   if attempt==2:break
 # A concurrent writer took the next version: report the conflict instead of skipping a number.
 raise _conflict(payload.base_version,_current_version(db,payload.run_id))
