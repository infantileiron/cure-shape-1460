import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import CurveDataset,AlignmentPolicy,ShapeStudy
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload):
 dataset=db.get(CurveDataset,payload.dataset_id);policy=db.get(AlignmentPolicy,payload.policy_id)
 if not dataset or not policy:raise HTTPException(404,"曲线集或对齐口径不存在")
 if db.scalar(select(ShapeStudy).where(ShapeStudy.name==payload.name)):raise HTTPException(409,"归并任务名称已存在")
 item=ShapeStudy(id=str(uuid.uuid4()),snapshot={'dataset':serialize(dataset),'policy':serialize(policy)},created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
