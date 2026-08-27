from pydantic import BaseModel, ValidationError, Field
from typing import Annotated, List, Optional

class PatientValidation(BaseModel):
    name: str = Field(max_length=100, title="Name of the patient", description="Maximum length of name is 100 characters")