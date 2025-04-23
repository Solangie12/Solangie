from fastapi import FastAPI, HTTPException, Request
import uvicorn
from app.controlador.PatientCrud import GetPatientById,WritePatient,GetPatientByIdentifier,WriteServiceRequest,read_service_request,write_appointment,read_appointment
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solo este dominio
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    status,patient = GetPatientById(patient_id)
    if status=='success':
        return patient  # Return patient
    elif status=='notFound':
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
    # Llama a la función auxiliar que obtiene la solicitud de servicio
    service_request = read_service_request(service_request_id)
    if service_request:
        return service_request
    else:
        raise HTTPException(status_code=404, detail="Solicitud de servicio no encontrada")
        

@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    new_patient_dict = dict(await request.json())
    status,patient_id = WritePatient(new_patient_dict)
    if status=='success':
        return {"_id":patient_id}  # Return patient id
    else:
        raise HTTPException(status_code=500, detail=f"Validating error: {status}")


@app.post("/service-request", response_model=dict)
async def add_service_request(request: Request):
    # Obtiene el JSON enviado en la solicitud POST
    service_request_data = await request.json()
    
    # Llama a la función que inserta la solicitud en la base de datos
    status, service_request_id = WriteServiceRequest(service_request_data)
    
    if status == "success":
        return {"_id": service_request_id}
    else:
        raise HTTPException(status_code=500, detail=f"Error al registrar la solicitud: {status}")

@app.post("/appointment", response_model=dict)
async def add_appointment(request: Request):
    # Obtiene el JSON enviado en la solicitud POST
    appointment_data = await request.json()
    
    # Llama a la función que inserta el appointment en la base de datos
    status, appointment_id = write_appointment(appointment_data)
    
    if status == "success":
        return {"_id": appointment_id}
    else:
        raise HTTPException(status_code=500, detail="Error al registrar la cita")

@app.get("/appointment/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: str):
    # Llama a la función que obtiene el appointment de la base de datos
    appointment = read_appointment(appointment_id)
    if appointment:
        return appointment
    else:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)