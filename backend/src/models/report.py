from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class Report(Base):
 __tablename__="reports"
 id:Mapped[str]=mapped_column(String,primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("shape_runs.id"))
 review_id:Mapped[str]=mapped_column(ForeignKey("cluster_reviews.id"),unique=True)
 review_version:Mapped[int]=mapped_column(Integer,nullable=True)
 title:Mapped[str]=mapped_column(String)
 snapshot:Mapped[dict]=mapped_column(JSON,default=dict,nullable=True)
 published_by:Mapped[str]=mapped_column(String)
 created_at:Mapped[str]=mapped_column(String)
