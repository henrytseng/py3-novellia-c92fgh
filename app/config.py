from pydantic import BaseModel
from typing import List
from enum import Enum


class ExtractableResources(Enum):
    ALL = "all"
    OBSERVATION = "Observation"
    PROCEDURE = "Procedure"
    CONDITION = "Condition"
    MEDICATION_REQUEST = "MedicationRequest"


class FieldConfig(BaseModel):
    """
    Represents a field configuration for a resource type
    """

    id: ExtractableResources
    subject: ExtractableResources
    code: ExtractableResources
    resourceType: ExtractableResources

    # Only Observation
    effectiveDateTime: List[ExtractableResources]
    valueQuantity: List[ExtractableResources]

    # Only Procedure
    performedDateTime: List[ExtractableResources]

    # Only MedicationRequest
    dosageInstruction: List[ExtractableResources]

    # Only Observation, Procedure, Condition, MedicationRequest
    status: List[ExtractableResources]


class ExtractionConfig(BaseModel):
    """
    Represents an extraction configuration
    """

    fields: FieldConfig
