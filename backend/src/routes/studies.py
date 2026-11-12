from fastapi import APIRouter,Depends,HTTPException,Response
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import ShapeStudy
from src.schemas.study import StudyInput
from src.services import studies as service
from src.utils.serialization import rows,serialize
router=APIRouter(prefix='/studies')
@router.get('')
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(ShapeStudy).order_by(ShapeStudy.created_at.desc())))
@router.post('')
def create(payload:StudyInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload)
