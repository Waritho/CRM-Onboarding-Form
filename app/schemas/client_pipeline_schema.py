from pydantic import BaseModel
from typing import List, Optional


# SUB STAGE
class SubStageCreate(BaseModel):
    name: str
    position: int
    is_enabled: bool = True


class SubStageResponse(SubStageCreate):
    id: int

    class Config:
        from_attributes = True


# STAGE
class StageCreate(BaseModel):
    name: str
    position: int
    comment: Optional[str] = None
    is_enabled: bool = True
    sub_stages: Optional[List[SubStageCreate]] = []


class StageResponse(StageCreate):
    id: int
    sub_stages: List[SubStageResponse]

    class Config:
        from_attributes = True


# TAG
class TagCreate(BaseModel):
    name: str
    is_enabled: bool = True


class TagResponse(TagCreate):
    id: int

    class Config:
        from_attributes = True


# FULL PIPELINE UPSERT
class PipelineConfigCreate(BaseModel):
    stages: List[StageCreate]
    tags: List[TagCreate]


class PipelineConfigResponse(BaseModel):
    stages: List[StageResponse]
    tags: List[TagResponse]