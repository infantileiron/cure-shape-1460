from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class PolicyInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 name:str=Field(min_length=2,max_length=120)
 normalization:Literal['raw','zscore']
 window:int=Field(ge=0,le=63,strict=True)
 threshold:float=Field(ge=0,le=1000000)
