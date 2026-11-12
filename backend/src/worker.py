from pathlib import Path
import redis,traceback
from sqlalchemy import select
from src.config.settings import REDIS_URL
from src.config.database import Session
from src.models import ShapeRun,ShapeStudy
from src.services.analysis import analyze
client=redis.Redis.from_url(REDIS_URL);heartbeat=Path('/artifacts/worker-heartbeat')
def execute(id):
 with Session() as db:
  run=db.get(ShapeRun,id)
  if not run or run.status not in ('queued','running'):return
  run.status='running';db.commit()
  try:
   run.result=analyze(db.get(ShapeStudy,run.study_id).snapshot);run.status='completed'
  except Exception as e:run.error=str(e);run.status='failed';traceback.print_exc()
  db.commit()
with Session() as db:
 for id in db.scalars(select(ShapeRun.id).where(ShapeRun.status.in_(['queued','running']))):client.lpush('cure-shape:jobs',id)
while True:
 heartbeat.touch();job=client.brpop('cure-shape:jobs',timeout=1)
 if job:execute(job[1].decode())
