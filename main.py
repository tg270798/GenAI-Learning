from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StrictInt, computed_field, field_validator
from typing import Optional, Annotated, List
import json

app = FastAPI() #creates an object of the FastAPI class, which is the main entry point for the application

# creating a pydantic model for the patient data, which will be used to validate the 
# incoming request data and generate the OpenAPI documentation

class Patient(BaseModel):
    id: Annotated[str, Field(description="Patient's unique identifier", example="P001")]
    name: Annotated[str, Field(description="Patient's name", example="John Doe")]
    city: Annotated[str, Field(description="Patient's city", example="New York")]
    age: Annotated[StrictInt, Field(gt=0, description="Patient's age", example=30)]
    gender: Annotated[str, Field(description="Patient's gender", example="male")]
    height: Annotated[float, Field(description="Patient's height in meters", example=1.75)]
    weight: Annotated[float, Field(description="Patient's weight in kilograms", example=70)]

    # computed field to calculate the BMI based on weight and height
    @computed_field
    @property
    def bmi(self) -> float:
        bmi_value = round(self.weight / (self.height ** 2), 2)
        return bmi_value

    # computed field to provide a verdict based on the BMI value
    @computed_field
    @property
    def bmi_verdict(self) -> str:
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "Underweight"
        elif 18.5 <= bmi_value < 24.9:
            return "Normal weight"
        elif 25 <= bmi_value < 29.9:
            return "Overweight"
        else:
            return "Obesity"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default = None)]
    city: Annotated[Optional[str], Field(default = None)]
    age: Annotated[Optional[StrictInt], Field(default = None)]
    gender: Annotated[Optional[str], Field(default = None)]
    height: Annotated[Optional[float], Field(default = None)]
    weight: Annotated[Optional[float], Field(default = None)]

@app.get("/") #signifies that this function will handle GET requests to the root URL ("/") of the application
def hello():
    return {"message": "Patient Management System"}

@app.get("/about")
def about():
    return {"message": "This is a Patient Management System API built with FastAPI."}


def load_data():
    # generates a dictionary of patient data from a JSON file
    with open("patients.json", "r") as file:
        data = json.load(file)

    return data

def save_data(data):
    # saves the patient data to a JSON file
    with open("patients.json", "w") as file:
        json.dump(data, file, indent=4)

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="ID of the patient for whom data is to be retrieved", example="P001")):
    data = load_data()

    if patient_id in data:
        return data[patient_id]

    raise HTTPException(status_code = 404, detail = "Patient Not found")
    # return{"error": "Patient not found."}

@app.get("/sort")
def patient_sort(field: str =  Query(..., description= "Data can be sorted based on City, Age or BMI", example = "age"), 
                 order: str = Query('asc',description = "order in which data is to be sorted", example = "asc")):


    valid_fields = ["city", "age", "bmi"]

    if field not in valid_fields:
        raise HTTPException(status_code=400, detail = f"Invalid field, {field}")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail = f"Invalid order, {order}")

    data= load_data()
    sorted_data = sorted(data.values(), key = lambda x: x.get(field,0), reverse = (order == "desc"))

    return sorted_data

@app.post("/add")
def add_record(patient: Patient): #patient is an instance of the Patient model, which will be automatically validated by FastAPI based on the defined fields and their types
    #load existing data
    data = load_data()

    #check for any existing record to avoid duplicate entries, if the patient ID already exists in the data, it raises an HTTPException with a 400 status code and a message indicating that the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail = f"Patient with ID {patient.id} already exists.")

    data[patient.id] = patient.model_dump(exclude=["id"]) 
    # model_dump converts pydantic Patient model instance to a python dictionary
    # exclude=["id"] excludes the id field from the dictionary, as it is already used as the key in the data dictionary. This ensures that the patient's ID is not duplicated in the stored data.
    # data[patient.id] = patient.model_dump(exclude=["id"]) creates a new entry in the data dictionary with the patient's ID as the key and the patient's data (excluding the ID) as the value. This allows for easy retrieval of patient records based on their unique identifier.

    save_data(data)
    return JSONResponse(status_code=201, content={"message": f"Patient with ID {patient.id} added successfully."})

@app.put("/update/{patient_id}")
def update_record(patient_id: str, patient_update: PatientUpdate):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = f"Patient with ID {patient_id} not found.")

    # Update the existing patient record with the new data
    existing_patient_data = data[patient_id]
    updated_patient_data = patient_update.model_dump(exclude_unset=True)  # Get only the fields that were provided in the request

    compute_bmi = False
    for key, value in updated_patient_data.items():
        existing_patient_data[key] = value

        if key in ["height", "weight"]:
            compute_bmi = True



    if compute_bmi:
        bmi_value = round(existing_patient_data["weight"] / (existing_patient_data["height"] ** 2), 2)
        existing_patient_data["bmi"] = bmi_value

        if bmi_value < 18.5:
            existing_patient_data["bmi_verdict"] = "Underweight"
        elif 18.5 <= bmi_value < 24.9:
            existing_patient_data["bmi_verdict"] = "Normal weight"
        elif 25 <= bmi_value < 29.9:
            existing_patient_data["bmi_verdict"] = "Overweight"
        else:
            existing_patient_data["bmi_verdict"] = "Obesity"

    data[patient_id] = existing_patient_data  # Update the patient record in the data dictionary

    save_data(data)
    return JSONResponse(status_code = 200, content={"message": f"Patient with ID {patient_id} updated successfully."})



@app.delete("/delete/{patient_id}")
def delete_record(patient_id: str):

    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = f"Patient with ID {patient_id} not found.")

    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code = 200, content={"message": f"Patient with ID {patient_id} deleted successfully."})

# uvicorn main:app --reload
