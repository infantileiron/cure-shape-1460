import uuid
from fastapi import HTTPException
from sqlalchemy import select,func
from src.models import ClusterReview
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload,user):
 run=require_completed(db,payload.run_id);expected={c['cluster_id'] for c in run.result['tree']['clusters']};names=payload.names
 if len(names)!=len(expected) or {n.get('cluster_id') for n in names}!=expected or any(set(n)!={'cluster_id','name'} or not n['name'].strip() or len(n['name'])>80 for n in names):raise HTTPException(422,'请为每个当前簇填写唯一对应的人工名称，保留完整簇ID')
 version=(db.scalar(select(func.max(ClusterReview.version)).where(ClusterReview.run_id==payload.run_id)) or 0)+1
 item=ClusterReview(id=str(uuid.uuid4()),version=version,created_at=now(),author=user['email'],**payload.model_dump());db.add(item);db.commit();return serialize(item)
