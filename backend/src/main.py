from contextlib import asynccontextmanager
import logging,redis
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from src.config.database import engine
from src.config.settings import SEED_DEMO,REDIS_URL
from src.middlewares.errors import ErrorMiddleware
from src.middlewares.audit import AuditMiddleware
from src.config.migrations import apply_compat_migrations
from src.routes import auth,datasets,policies,studies,runs,reviews,reports,audit
@asynccontextmanager
async def lifespan(app):
 apply_compat_migrations()
 if SEED_DEMO:
  try:
   from scripts.seed_demo import seed
   seed()
  except Exception:logging.exception('seed failed')
 yield
app=FastAPI(title='滩原 · 固化曲线形态归并',lifespan=lifespan)
@app.exception_handler(RequestValidationError)
async def invalid_input(request,error):
 details=['.'.join(str(x) for x in item['loc'])+': '+item['msg'] for item in error.errors()]
 return JSONResponse({'detail':'输入校验失败：'+'；'.join(details)},status_code=422)
app.add_middleware(AuditMiddleware);app.add_middleware(ErrorMiddleware)
for module in (auth,datasets,policies,studies,runs,reviews,reports,audit):app.include_router(module.router)
@app.get('/health')
def health():
 with engine.connect() as db:db.execute(text('SELECT 1'))
 redis.Redis.from_url(REDIS_URL).ping();return {'status':'ok'}
