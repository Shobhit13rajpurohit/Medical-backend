from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db
from typing import List, Optional
import shutil
import os
import uuid
from fastapi.responses import FileResponse

# Create an images directory if it doesn't exist
UPLOAD_DIR = "uploads/doctor_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("/", response_model=List[schemas.DoctorResponse])
def get_doctors(db: Session = Depends(get_db)):
    return crud.get_doctors(db)

@router.post("/", response_model=schemas.DoctorResponse)
async def create_doctor(
    name: str = Form(...),
    specialization: str = Form(...),
    phone: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Create a doctor object from form data
    doctor_data = schemas.DoctorCreate(
        name=name,
        specialization=specialization,
        phone=phone
    )
    
    # Handle image upload if provided
    image_filename = None
    if image:
        # Generate a unique filename to prevent collisions
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_filename = unique_filename
    
    # Create the doctor in the database
    new_doctor = crud.create_doctor(db, doctor_data, image_filename)
    return new_doctor

@router.put("/{doctor_id}", response_model=schemas.DoctorResponse)
async def update_doctor(
    doctor_id: int,
    name: str = Form(...),
    specialization: str = Form(...),
    phone: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Create a doctor object from form data
    doctor_data = schemas.DoctorCreate(
        name=name,
        specialization=specialization,
        phone=phone
    )
    
    # Get the existing doctor to check if we need to delete an old image
    existing_doctor = crud.get_doctor(db, doctor_id)
    if not existing_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Handle image upload if provided
    image_filename = existing_doctor.image_filename  # Keep existing image by default
    if image:
        # Delete the old image if it exists
        if existing_doctor.image_filename:
            old_image_path = os.path.join(UPLOAD_DIR, existing_doctor.image_filename)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        # Save the new image
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_filename = unique_filename
    
    # Update the doctor in the database
    updated_doctor = crud.update_doctor(db, doctor_id, doctor_data, image_filename)
    if not updated_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return updated_doctor

@router.delete("/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    # Get the doctor to retrieve the image filename
    doctor = crud.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Delete the image file if it exists
    if doctor.image_filename:
        image_path = os.path.join(UPLOAD_DIR, doctor.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Delete the doctor from the database
    result = crud.delete_doctor(db, doctor_id)
    if not result:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return {"message": "Doctor deleted successfully"}

@router.get("/images/{filename}")
async def get_doctor_image(filename: str):
    """Serve doctor images"""
    image_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path)

@router.get("/{doctor_id}/patient-count", response_model=dict)
def get_doctor_patient_count(doctor_id: int, db: Session = Depends(get_db)):
    """Get the count of unique patients who visited a specific doctor"""
    # Get all unique patients
    unique_patients = crud.get_unique_patients(db)
    
    # Count how many unique patients visited this doctor
    count = sum(1 for patient in unique_patients if doctor_id in patient["doctor_visits"])
    
    return {
        "doctor_id": doctor_id,
        "unique_patient_count": count,
        "total_visits": len(crud.get_visits(db, doctor_id))
    }