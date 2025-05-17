from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

from app.controlador.PatientCrud import (
    GetPatientById, WritePatient, GetPatientByIdentifier,
    WriteServiceRequest, read_service_request, write_appointment,
    read_appointment, write_clinical_procedure
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
@app.on_event("startup")
async def startup_event():
    print("🚀 ¡Aplicación FastAPI iniciada correctamente!")

# ------------------------ CONFIGURACIÓN CORS Y STATIC -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------------- MODELOS PARA FORMULARIO MÉDICO ----------------------
class Medication(BaseModel):
    name: str
    dose: str
    frequency: str
    route: str

class MedicalForm(BaseModel):
    doctorName: str
    specialty: str
    institution: str
    patientName: str
    documentType: str
    documentNumber: str
    age: int
    sex: str
    mainDiagnosis: str
    procedureDone: str
    procedureName: str
    procedureCode: Optional[str] = None
    procedureDate: str
    procedureTime: str
    procedureType: Optional[str] = None
    procedureDescription: str
    technique: Optional[str] = None
    anesthesia: Optional[str] = None
    patientStatus: Optional[str] = None
    followUp: Optional[str] = None
    medications: Optional[List[Medication]] = []

# ------------------------- ENDPOINTS EXISTENTES -----------------------------

@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    status, patient = GetPatientById(patient_id)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
    print("received", system, value)
    status, patient = GetPatientByIdentifier(system, value)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.get("/service-request/{service_request_id}", response_model=dict)
async def get_service_request(service_request_id: str):
    service_request = read_service_request(service_request_id)
    if service_request:
        return service_request
    else:
        raise HTTPException(status_code=404, detail="Solicitud de servicio no encontrada")

@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    new_patient_dict = dict(await request.json())
    status, patient_id = WritePatient(new_patient_dict)
    if status == 'success':
        return {"_id": patient_id}
    else:
        raise HTTPException(status_code=500, detail=f"Validating error: {status}")

@app.post("/service-request", response_model=dict)
async def add_service_request(request: Request):
    service_request_data = await request.json()
    status, service_request_id = WriteServiceRequest(service_request_data)
    if status == "success":
        return {"_id": service_request_id}
    else:
        raise HTTPException(status_code=500, detail=f"Error al registrar la solicitud: {status}")

@app.post("/appointment", response_model=dict)
async def add_appointment(request: Request):
    appointment_data = await request.json()
    status, appointment_id = write_appointment(appointment_data)
    if status == "success":
        return {"_id": appointment_id}
    else:
        raise HTTPException(status_code=500, detail="Error al registrar la cita")

@app.get("/appointment/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: str):
    appointment = read_appointment(appointment_id)
    if appointment:
        return appointment
    else:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

@app.post("/clinical-procedure", response_model=dict)
async def register_clinical_procedure(request: Request):
    procedure_data = await request.json()
    status, procedure_id = write_clinical_procedure(procedure_data)
    if status == "success":
        return {"_id": procedure_id}
    else:
        raise HTTPException(status_code=500, detail="Error al registrar procedimiento y medicamentos")

# ------------------ NUEVOS ENDPOINTS PARA FORMULARIO HTML -------------------
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("formulario.html", {"request": request})

@app.post("/submit-form", response_model=dict)
async def submit_form(data: MedicalForm):
    try:
        status, procedure_id = write_clinical_procedure(data.dict())
        if status == "success":
            return {"message": "Formulario recibido correctamente", "_id": procedure_id}
        else:
            raise HTTPException(status_code=500, detail="Error al guardar formulario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------- EJECUCIÓN LOCAL -------------------------------
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
