from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ShapeStudy(Base):
 __tablename__="shape_studies"
 id:Mapped[str]=mapped_column(String,primary_key=True)
 name:Mapped[str]=mapped_column(String,unique=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey("curve_datasets.id"))
 policy_id:Mapped[str]=mapped_column(ForeignKey("alignment_policies.id"))
 snapshot:Mapped[dict]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String)
