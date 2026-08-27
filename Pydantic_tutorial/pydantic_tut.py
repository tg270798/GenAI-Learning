from pydantic import BaseModel, StrictInt, EmailStr, Field, ValidationError
from typing import List, Optional, Annotated

class PatientValidation(BaseModel):
    name: Annotated[str, Field(max_length = 100, title = "Name of the patient", description="Maximum length of name is 100 characters")]
    age: Annotated[StrictInt, Field(gt=0, description="Age must be a positive integer")]
    email: Annotated[EmailStr, Field(description ="Email address of the patient")]
    weight: Annotated[float, Field(gt=0, description="Weight must be a positive number")]
    bmi: Annotated[float, Field(gt=0, description="BMI must be a positive number")]
    allergies: Annotated[Optional[List[str]],Field(default= None, description = "List of allergies, if any")]
    details: Annotated[dict, Field(description="Additional details about the patient")]

def insert_data(patient: PatientValidation):
    print(patient.name)
    print(patient.age)
    print(patient.email)
    print(patient.weight)
    print(patient.bmi)
    print(patient.allergies)
    print(patient.details)
    print("data inserted")

patient_info = {
                'name':'tathagat' 
            ,    'age':28
            ,    'email':'tathagat@example.com'
            ,    'weight':70.5
            ,    'bmi':25.0
            ,    'allergies': ['penicillin']
            ,    'details': {'occupation': 'engineer', 'city': 'New York', 'contact': '123-456-7890'}
                }


patient1 = PatientValidation(**patient_info)

try:
    insert_data(patient1)
except ValidationError as e:
    print("Validation errors:")
    for error in e.errors():
        print(f"  {error['loc'][0]}: {error['msg']}")