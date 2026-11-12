-- Declarative schema source: src/models/*.py
-- Initial startup uses SQLAlchemy metadata.create_all; no destructive migration or seed overwrite.
-- Six domain tables + users + audit_events; immutable snapshots and review versions.

-- Review versioning and archive snapshot (applied idempotently by src/config/migrations.py):
-- cluster_reviews.base_version INTEGER DEFAULT 0         -- page baseline at save time
-- cluster_reviews UNIQUE (run_id, version)               -- contiguous, never duplicated numbers
-- reports.review_version INTEGER                         -- approved review version
-- reports.snapshot JSON                                  -- frozen names/checksum/clusters/policy
