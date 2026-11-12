from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ClusterReview(Base):
 __tablename__="cluster_reviews"
 __table_args__=(UniqueConstraint("run_id","version",name="uq_cluster_review_run_version"),)
 id:Mapped[str]=mapped_column(String,primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("shape_runs.id"))
 version:Mapped[int]=mapped_column(Integer)
 base_version:Mapped[int]=mapped_column(Integer,default=0)
 names:Mapped[list]=mapped_column(JSON)
 note:Mapped[str]=mapped_column(Text)
 decision:Mapped[str]=mapped_column(String)
 author:Mapped[str]=mapped_column(String)
 created_at:Mapped[str]=mapped_column(String)
