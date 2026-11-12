from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class AlignmentPolicy(Base):
 __tablename__="alignment_policies"
 id:Mapped[str]=mapped_column(String,primary_key=True)
 name:Mapped[str]=mapped_column(String,unique=True)
 normalization:Mapped[str]=mapped_column(String)
 window:Mapped[int]=mapped_column(Integer)
 threshold:Mapped[float]=mapped_column(Double)
 created_at:Mapped[str]=mapped_column(String)
