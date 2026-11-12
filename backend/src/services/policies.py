import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import AlignmentPolicy
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload):
 if db.scalar(select(AlignmentPolicy).where(AlignmentPolicy.name==payload.name)):raise HTTPException(409,"对齐口径名称已存在")
 item=AlignmentPolicy(id=str(uuid.uuid4()),created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
