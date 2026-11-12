import uuid,csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import Report,ClusterReview,ShapeStudy
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload,user):
 require_completed(db,payload.run_id)
 review=db.scalar(select(ClusterReview).where(ClusterReview.run_id==payload.run_id).order_by(ClusterReview.version.desc()))
 if not review or review.decision!='accepted':raise HTTPException(409,'最新版本人工命名复核须接受后才能归档')
 if db.scalar(select(Report).where(Report.review_id==review.id)):raise HTTPException(409,'此复核版本已归档')
 item=Report(id=str(uuid.uuid4()),review_id=review.id,published_by=user['email'],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,'归档不存在')
 run=require_completed(db,report.run_id);review=db.get(ClusterReview,report.review_id);result=run.result;names={n['cluster_id']:n['name'] for n in review.names};buf=io.StringIO();writer=csv.DictWriter(buf,['run_id','checksum','review_version','curve_id','cluster_id','human_name','cluster_diameter','threshold','normalization','window','distance_definition']);writer.writeheader()
 for c in result['tree']['clusters']:
  for cid in c['members']:writer.writerow({'run_id':run.id,'checksum':result['checksum'],'review_version':review.version,'curve_id':cid,'cluster_id':c['cluster_id'],'human_name':names[c['cluster_id']],'cluster_diameter':c['diameter'],'threshold':result['policy']['threshold'],'normalization':result['policy']['normalization'],'window':result['policy']['window'],'distance_definition':'sqrt(minimum cumulative squared cost / chosen optimal path length)'})
 return '\ufeff'+buf.getvalue()
