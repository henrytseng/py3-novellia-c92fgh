"""
Transformation data models
"""

from pydantic import BaseModel, Field
from app.transformations.extract import extract_field
from app.transformations.flatten import flatten_nested


ACTION_MAPPING = {
    "extract": extract_field,
    "flatten": flatten_nested,
}


class TransformationCriteria(BaseModel):
    """
    A transformation action
    """

    action: str
    field: str
    as_field: str | None = Field(alias="as", default=None)
