from pydantic import BaseModel,Field,ConfigDict
class CurveInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 curve_id:str=Field(min_length=1,max_length=21)
 label:str=Field(min_length=1,max_length=80)
 values:list[float]=Field(min_length=64,max_length=64)
class DatasetInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 name:str=Field(min_length=2,max_length=120)
 source:str=Field(min_length=2,max_length=120)
 times:list[float]=Field(min_length=64,max_length=64)
 curves:list[CurveInput]=Field(min_length=2,max_length=64)
