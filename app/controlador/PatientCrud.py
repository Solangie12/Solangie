from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
import json

# Conexión a la base de datos
collection = connect_to_mongodb("SamplePatientService", "patients")
service_requests_collection = connect_to_mongodb("SamplePatientService", "service_requests")
appointment_collection = connect_to_mongodb("SamplePatientService", "appointment")
clinical_procedure_collection = connect_to_mongodb("SamplePatientService", "clinical_procedure")
medication_collection = connect_to_mongodb("SamplePatientService", "medication")


def GetPatientById(patient_id: str):
    try:
        patient = collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        print("Error in GetPatientById:", e)
        return "notFound", None


def WritePatient(patient_dict: dict):
    try:
        pat = Patient.model_validate(patient_dict)
    except Exception as e:
        print("Error validating patient:", e)
        return f"errorValidating: {str(e)}", None
    validated_patient_json = pat.model_dump()
    result = collection.insert_one(validated_patient_json)
    if result:
        inserted_id = str(result.inserted_id)
        return "success", inserted_id
    else:
        return "errorInserting", None


def GetPatientByIdentifier(patientSystem, patientValue):
    try:
        patient = collection.find_one({
            "identifier": {
                "$elemMatch": {
                    "system": patientSystem,
                    "value": patientValue
                }
            }
        })
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        print("Error in GetPatientByIdentifier:", e)
        return "notFound", None


def WriteServiceRequest(service_request_data: dict):
    try:
        result = service_requests_collection.insert_one(service_request_data)
        return "success", str(result.inserted_id)
    except Exception as e:
        print("Error in WriteServiceRequest:", e)
        return "error", None


def read_service_request(service_request_id: str) -> dict:
    try:
        query = {"_id": ObjectId(service_request_id)}
    except Exception as e:
        print("Error al convertir el ID:", e)
        return None

    service_request = service_requests_collection.find_one(query)
    if service_request:
        service_request["_id"] = str(service_request["_id"])
        return service_request
    else:
        return None


def GetAppointmentByIdentifier(appointmentSystem, appointmentValue):
    try:
        appointment = appointment_collection.find_one({
            "identifier": {
                "$elemMatch": {
                    "system": appointmentSystem,
                    "value": appointmentValue
                }
            }
        })
        if appointment:
            appointment["_id"] = str(appointment["_id"])
            return "success", appointment
        return "notFound", None
    except Exception as e:
        print("Error en GetAppointmentByIdentifier:", e)
        return "notFound", None


def write_appointment(appointment_data: dict):
    try:
        # Procesar datos básicos
        patient_name = appointment_data.get("patientName", "Desconocido")
        appointment_date = appointment_data.get("appointmentDate")
        appointment_time = appointment_data.get("appointmentTime")
        reason = appointment_data.get("reason", "")

        # Construir estructura tipo FHIR
        appointment_fhir = {
            "resourceType": "Appointment",
            "status": "booked",
            "description": reason,
            "start": f"{appointment_date}T{appointment_time}",
            "participant": [
                {
                    "actor": {
                        "display": patient_name
                    },
                    "status": "accepted"
                }
            ]
        }

        result = appointment_collection.insert_one(appointment_fhir)
        print("✅ Resultado MongoDB:", result)
        return "success", str(result.inserted_id)


    except Exception as e:
        print("Error in write_appointment:", e)
        return "error", None


def read_appointment(appointment_id: str) -> dict:
    try:
        query = {"_id": ObjectId(appointment_id)}
    except Exception as e:
        print("Error al convertir el ID:", e)
        return None

    appointment = appointment_collection.find_one(query)
    if appointment:
        appointment["_id"] = str(appointment["_id"])
        return appointment
    else:
        return None


# --- NUEVAS FUNCIONES PARA PROCEDIMIENTOS Y MEDICAMENTOS ---


def write_clinical_procedure(procedure_data: dict):
    try:
        print("Recibido procedimiento clínico:", procedure_data)  # Agrega esto

        result = clinical_procedure_collection.insert_one(procedure_data)
        print(f"Inserted clinical procedure ID: {result.inserted_id}")
        return "success", str(result.inserted_id)
    except Exception as e:
        print("Error in write_clinical_procedure:", e)
        return "error", None


def write_medication(medication_data: dict):
    try:
        result = medication_collection.insert_one(medication_data)
        return "success", str(result.inserted_id)
    except Exception as e:
        print("Error in write_medication:", e)
        return "error", None


def get_clinical_procedures_by_patient(patient_id: str):
    try:
        query = {"subject.reference": f"Patient/{patient_id}"}
        results = list(clinical_procedure_collection.find(query))
        for procedure in results:
            procedure["_id"] = str(procedure["_id"])
        return results
    except Exception as e:
        print("Error in get_clinical_procedures_by_patient:", e)
        return []


def get_clinical_procedures_by_service_request(service_request_id: str):
    try:
        query = {"basedOn.reference": f"ServiceRequest/{service_request_id}"}
        results = list(clinical_procedure_collection.find(query))
        for procedure in results:
            procedure["_id"] = str(procedure["_id"])
        return results
    except Exception as e:
        print("Error in get_clinical_procedures_by_service_request:", e)
        return []


def get_medications_by_patient(patient_id: str):
    try:
        query = {"subject.reference": f"Patient/{patient_id}"}
        results = list(medication_collection.find(query))
        for medication in results:
            medication["_id"] = str(medication["_id"])
        return results
    except Exception as e:
        print("Error in get_medications_by_patient:", e)
        return []


def get_medications_by_service_request(service_request_id: str):
    try:
        query = {"basedOn.reference": f"ServiceRequest/{service_request_id}"}
        results = list(medication_collection.find(query))
        for medication in results:
            medication["_id"] = str(medication["_id"])
        return results
    except Exception as e:
        print("Error in get_medications_by_service_request:", e)
        return []
