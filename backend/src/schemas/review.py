from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class ReviewInput(BaseModel):
 model_config=ConfigDict(extra='forbid')
 run_id:str
 # Version the page was opened on; 0 means no review existed when the form was opened.
 base_version:int=Field(ge=0)
 note:str=Field(min_length=10,max_length=2000)
 decision:Literal['accepted','needs_changes']
 names:list[dict[str,str]]
