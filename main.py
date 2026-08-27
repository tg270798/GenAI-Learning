from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI() #creates an object of the FastAPI class, which is the main entry point for the application

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



