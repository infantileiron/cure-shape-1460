import uuid,redis
from fastapi import HTTPException
from src.models import ShapeRun,ShapeStudy
from src.config.settings import REDIS_URL
from src.utils.time import now
from src.utils.serialization import serialize

def create(db,study_id):
 if not db.get(ShapeStudy,study_id):raise HTTPException(404,"归并任务不存在")
 item=ShapeRun(id=str(uuid.uuid4()),study_id=study_id,status='queued',result={},error='',created_at=now());db.add(item);db.commit()
 try:redis.Redis.from_url(REDIS_URL).lpush('cure-shape:jobs',item.id)
 except redis.RedisError:
  item.status='failed';item.error='队列不可用，请重试';db.commit();raise HTTPException(503,item.error)
 return serialize(item)
def require_completed(db,id):
 item=db.get(ShapeRun,id)
 if not item:raise HTTPException(404,'运行不存在')
 if item.status!='completed':raise HTTPException(409,'运行尚未成功完成')
 return item
