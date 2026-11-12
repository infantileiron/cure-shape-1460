from sqlalchemy import inspect,text
from sqlalchemy.exc import IntegrityError
import logging
from src.config.database import engine
from src.config.database import Base

def apply_compat_migrations(target=engine):
 """Idempotently add review-versioning columns for databases created before this change.
 Fresh databases already get them from Base.metadata.create_all; existing demo volumes keep
 their rows because every step only adds a column or a unique index.
 """
 Base.metadata.create_all(target)
 inspector=inspect(target)
 tables=inspector.get_table_names()
 if "cluster_reviews" in tables:
  columns={c["name"] for c in inspector.get_columns("cluster_reviews")}
  with target.begin() as conn:
   if "base_version" not in columns:
    conn.execute(text("ALTER TABLE cluster_reviews ADD COLUMN base_version INTEGER DEFAULT 0"))
   # Legacy rows keep base_version 0: their opening context is unknown, so a later stale page
   # must conflict with them rather than inherit an invented baseline.
   try:
    with conn.begin_nested():
     conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_cluster_review_run_version ON cluster_reviews (run_id, version)"))
   except IntegrityError:
    # A savepoint keeps the column additions above valid on PostgreSQL, where a failed statement
    # would otherwise poison the whole transaction. Do not abort startup: the service still
    # refuses new duplicate versions from these legacy rows.
    logging.warning("legacy cluster_reviews rows share version numbers; unique index not created until duplicates are reconciled")
 if "reports" in tables:
  columns={c["name"] for c in inspector.get_columns("reports")}
  with target.begin() as conn:
   if "review_version" not in columns:
    conn.execute(text("ALTER TABLE reports ADD COLUMN review_version INTEGER"))
   if "snapshot" not in columns:
    conn.execute(text("ALTER TABLE reports ADD COLUMN snapshot JSON"))
   conn.execute(text("UPDATE reports SET review_version=(SELECT version FROM cluster_reviews WHERE cluster_reviews.id=reports.review_id) WHERE review_version IS NULL"))
