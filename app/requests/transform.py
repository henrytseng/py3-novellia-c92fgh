"""
API Request data models
"""

from typing import List

from pydantic import BaseModel

from app.transformations.schema import TransformationCriteria


class FilterQuery(BaseModel):
    id: str | None = None
    subject: str | None = None
    code: str | None = None


class RequestTransform(BaseModel):
    resourceTypes: List[str]
    transformations: List[TransformationCriteria]
    filters: FilterQuery
