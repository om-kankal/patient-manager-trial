from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, computed_field 
from typing import Annotated, Literal, Optional
import json
from fastapi.responses import JSONResponse

app = FastAPI()

json_path = 'v5.json'

class ThePatient(BaseModel):
    id:Annotated[str,Field(...,description="enter the ID of Patient")]
    name: Annotated[str,Field(...,description="enter the Patient name")]
    city: Annotated[str,Field(...,description="city of the patient")]
    age: Annotated[int,Field(...,gt=0,le=120, description="current age of the patient")]
    height: Annotated[float,Field(...,gt=0, description="height in meters")]
    weight: Annotated[float,Field(...,gt=0, description="weight of the patient in kg")]
    gender: Annotated[Literal['Male','Female','Other'], Field(...)]

    @computed_field
    @property
    def BMI(self)-> float:
        bmi = round(self.weight/ (self.height**2),2)
        return bmi


    @computed_field
    @property
    def verdict(self)->str:

        if self.BMI < 18.5:
            return 'Under Weight'

        elif self.BMI < 30:
            return  'Normal'

        else:
            return 'Observation required..'

def load_data():
    try:
        with open(json_path,'r') as file:
            data = json.load(file)
        return data
    except Exception:
        return{}


def save_data(data):
    try:
        with open(json_path,'w') as file:
            json.dump(data,file)
    except Exception:
        return{}


@app.get("/")
def welcome():
    return {
        'messege':"welcome to the root page sir"
    }

@app.get('/about')
def about():
    return{
        'about':'temp about page'
    }

@app.get('/health')
def health_check():
    return {
        'status':'ok',
        'version':'V001',
        'model_loaded':True
    }

@app.get('/patients')
def allPatient():
    data = load_data()
    return data

@app.post("/create")
def CreatePatient(patient: ThePatient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=404, detail = f"patient of ID {patient.id} already exists")

    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)
    return JSONResponse(status_code=200,
                        content={'messege':'patient added successfully'})


class PatientUpdate(BaseModel):
    name: Annotated[Optional[str],Field(description="enter the Patient name", default=None)]
    city: Annotated[Optional[str],Field(description="city of the patient", default=None)]
    age: Annotated[Optional[int],Field(gt=0,le=120, description="current age of the patient", default=None)]
    height: Annotated[Optional[float],Field(gt=0, description="height in meters", default=None)]
    weight: Annotated[Optional[float],Field(gt=0, description="weight of the patient in kg", default=None)]
    gender:Annotated[Optional[Literal['Male','Female','Other']],Field(default='Male')]



@app.put('/edit/{patient_id}')
def updatePatient(patient_id:str, patientupdate:PatientUpdate):
    
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=400, detail="patient not found..")

    existing_data = data[patient_id].copy()

    updated = patientupdate.model_dump(exclude_unset=True)
    
    for key,values in updated.items():
        existing_data[key] = values

    existing_data['id'] = patient_id
    
    patient_pydantic = ThePatient(**existing_data)

    existing_data = patient_pydantic.model_dump(exclude='id')

    data[patient_id] = existing_data

    save_data(data)

    return JSONResponse(
        status_code=200,
        content ={"messege":"data updated successfully"}
    ) 



@app.delete("/delete_one/{patient_id}")
def deletePatient(patient_id:str):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            content={'messege':"patient not found.."}
        ) 
    del data[patient_id]
    
    save_data(data)

    return JSONResponse(
        status_code=200,
        content = {'messege':'patient Deleted..'}
    )