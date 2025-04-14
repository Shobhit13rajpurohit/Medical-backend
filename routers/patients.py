# patients.py - Fixed with consistent routing

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db
from typing import List
router = APIRouter(prefix="/patients", tags=["Patients"])

# Get all patients endpoint
@router.get("/", response_model=List[schemas.PatientResponse])
def get_all_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all patients in the system (not filtered by visit)"""
    return crud.get_all_patients(db, skip, limit)

# Get patients by visit ID
@router.get("/{visit_id}", response_model=List[schemas.PatientResponse])
def get_patients_by_visit(visit_id: int, db: Session = Depends(get_db)):
    """Get patients for a specific visit"""
    patients = crud.get_patients(db, visit_id)
    print(f"Fetching patients for visit ID {visit_id}: Found {len(patients)}")
    return patients

# Create patient for a visit
@router.post("/{visit_id}", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(visit_id: int, patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient for a specific visit"""
    serial_no = len(crud.get_patients(db, visit_id)) + 1
    return crud.create_patient(db, patient, visit_id, serial_no)

# Toggle fee status
@router.patch("/patient/{patient_id}", response_model=schemas.PatientResponse)
def toggle_fee_status(patient_id: int, db: Session = Depends(get_db)):
    """Toggle fee status between 'paid' and 'due'"""
    updated_patient = crud.toggle_patient_fee_status(db, patient_id)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@router.put("/patient/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: int, 
    patient_update: schemas.PatientUpdate, 
    db: Session = Depends(get_db)
):
    """Update a patient's information"""
    updated_patient = crud.update_patient(db, patient_id, patient_update)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

# Delete patient
@router.delete("/patient/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient"""
    result = crud.delete_patient(db, patient_id)
    if not result:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

# Add this to patients.py

@router.get("/unique/", response_model=List[dict])
def get_unique_patients(db: Session = Depends(get_db)):
    """Get all unique patients with their doctor visits"""
    # Get all patients
    all_patients = crud.get_all_patients(db)
    
    # Create a map to track unique patients
    unique_patients_map = {}
    
    for patient in all_patients:
        # Create a unique key based on name and contact
        key = f"{patient.name}-{patient.contact}"
        
        # Get visit information
        visit = crud.get_visit(db, patient.visit_id)
        doctor_id = visit.doctor_id if visit else None
        
        if key not in unique_patients_map:
            # First time seeing this patient
            unique_patients_map[key] = {
                "id": patient.id,
                "name": patient.name,
                "contact": patient.contact,
                "feeStatus": patient.fee_status,
                "visitId": patient.visit_id,
                "serialNo": patient.serial_no,
                "doctorVisits": [doctor_id] if doctor_id else []
            }
        else:
            # We've seen this patient before
            if doctor_id and doctor_id not in unique_patients_map[key]["doctorVisits"]:
                unique_patients_map[key]["doctorVisits"].append(doctor_id)
    
    # Convert the map to a list
    unique_patients = list(unique_patients_map.values())
    
    return unique_patients

# Update the endpoint in patients.py

@router.get("/unique/", response_model=List[schemas.UniquePatientResponse])
def get_unique_patients(db: Session = Depends(get_db)):
    """Get all unique patients with their doctor visits"""
    return crud.get_unique_patients(db)

from typing import List


@router.get("/unique/", response_model=List[dict])
def get_unique_patients(db: Session = Depends(get_db)):
    """
    Get all unique patients with their doctor visits.
    A patient is considered unique based on their name and contact information.
    """
    return crud.get_unique_patients(db)