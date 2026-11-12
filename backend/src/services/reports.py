import uuid,csv,io
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError,OperationalError
from fastapi import HTTPException
from src.models import Report,ClusterReview,ShapeRun
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def _snapshot(run,review,title):
 return {'run_id':run.id,'checksum':run.result['checksum'],'review_id':review.id,'review_version':review.version,'title':title,'names':review.names,'clusters':run.result['tree']['clusters'],'policy':run.result['policy']}

def _latest(db,run_id):return db.scalar(select(ClusterReview).where(ClusterReview.run_id==run_id).order_by(ClusterReview.version.desc()))

def create(db,payload,user):
 require_completed(db,payload.run_id)
 review=db.get(ClusterReview,payload.review_id)
 if not review or review.run_id!=payload.run_id:raise HTTPException(404,'所选复核版本不属于该运行')
 # Only the newest accepted review may be approved; an older version has been superseded.
 latest=_latest(db,payload.run_id)
 if review.version!=latest.version:raise HTTPException(409,f'复核版本冲突：所选 v{review.version} 已有更新复核 v{latest.version}；请批准当前最新版本或重新提交')
 if review.decision!='accepted':raise HTTPException(409,'所选复核版本结论为待补充，须接受后才能归档')
 if db.scalar(select(Report).where(Report.review_id==review.id)):raise HTTPException(409,'此复核版本已归档')
 # Lock the run row so no later review can slip in between the latest check and the archive insert.
 try:db.execute(select(ShapeRun.id).where(ShapeRun.id==payload.run_id).with_for_update())
 except OperationalError:
  db.rollback();raise HTTPException(409,'复核版本正在变化，请刷新后重试')
 latest_after=_latest(db,payload.run_id)
 if latest_after.version!=review.version:raise HTTPException(409,f'复核版本冲突：所选 v{review.version} 已有更新复核 v{latest_after.version}；请批准当前最新版本或重新提交')
 run=require_completed(db,payload.run_id)
 item=Report(id=str(uuid.uuid4()),review_version=review.version,snapshot=_snapshot(run,review,payload.title),published_by=user['email'],created_at=now(),**payload.model_dump())
 db.add(item)
 try:db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,'此复核版本已归档或已有更新复核，请刷新后重试')
 return serialize(item)

def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,'归档不存在')
 # Archived reports keep the name, version, checksum and cluster membership captured at
 # approval time; later reviews or reruns cannot change an already downloaded CSV.
 snapshot=report.snapshot or {}
 run=require_completed(db,report.run_id);review=db.get(ClusterReview,report.review_id);result=run.result
 stored_names=snapshot.get('names') or (review.names if review else [])
 if isinstance(stored_names,list):stored_names={n['cluster_id']:n['name'] for n in stored_names}
 revision=snapshot.get('review_version') or report.review_version or (review.version if review else 0)
 checksum=snapshot.get('checksum') or result['checksum']
 clusters=snapshot.get('clusters') or result['tree']['clusters']
 policy=snapshot.get('policy') or result['policy']
 buf=io.StringIO();writer=csv.DictWriter(buf,['run_id','checksum','review_version','curve_id','cluster_id','human_name','cluster_diameter','threshold','normalization','window','distance_definition']);writer.writeheader()
 for c in clusters:
  for cid in c.get('members',[]):writer.writerow({'run_id':report.run_id,'checksum':checksum,'review_version':revision,'curve_id':cid,'cluster_id':c['cluster_id'],'human_name':stored_names.get(c['cluster_id'],''),'cluster_diameter':c.get('diameter',''),'threshold':policy.get('threshold'),'normalization':policy.get('normalization'),'window':policy.get('window'),'distance_definition':'sqrt(minimum cumulative squared cost / chosen optimal path length)'})
 return '﻿'+buf.getvalue()
