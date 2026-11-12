import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import CurveDataset
from src.utils.serialization import serialize
from src.utils.time import now
from src.services.preprocessing import validate_dataset

def create(db,payload):
 data=payload.model_dump()
 try:validate_dataset(data['times'],data['curves'])
 except ValueError as e:raise HTTPException(422,str(e))
 if db.scalar(select(CurveDataset).where(CurveDataset.name==payload.name)):raise HTTPException(409,"曲线集名称已存在")
 item=CurveDataset(id=str(uuid.uuid4()),created_at=now(),**data);db.add(item);db.commit();return serialize(item)
