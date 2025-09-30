from typing import List

from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class AssignTagsRequest(BaseModel):
    tag_ids: List[int]
