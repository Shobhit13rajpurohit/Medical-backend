# schedules.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time
import crud, schemas
from database import get_db
import shutil
import os
from pydantic import parse_obj_as

router = APIRouter(
    prefix="/schedules",
    tags=["schedules"]
)

# Define upload directory
UPLOAD_DIR = "uploads/doctors"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[schemas.DoctorScheduleResponse])
def get_schedules(db: Session = Depends(get_db)):
    """
    Get all doctor schedules
    """
    schedules = crud.get_schedules(db)
    return schedules

@router.post("/", response_model=schemas.DoctorScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    name: str = Form(...),
    specialization: str = Form(...),
    day_of_week: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    is_available: bool = Form(True),
    specific_date: Optional[str] = Form(None),
    contact_number: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a doctor schedule with image upload
    """
    # Handle image upload if provided
    image_filename = None
    if image and image.filename:
        # Save the uploaded file
        file_extension = os.path.splitext(image.filename)[1]
        image_filename = f"{name.replace(' ', '_')}_{os.urandom(4).hex()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, image_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    
    # Parse time strings
    start_time_obj = time.fromisoformat(start_time)
    end_time_obj = time.fromisoformat(end_time)
    
    # Parse date if provided
    specific_date_obj = None
    if specific_date:
        specific_date_obj = date.fromisoformat(specific_date)
    
    # Create schedule data
    schedule_data = {
        "name": name,
        "specialization": specialization,
        "day_of_week": day_of_week,
        "start_time": start_time_obj,
        "end_time": end_time_obj,
        "is_available": is_available,
        "specific_date": specific_date_obj,
        "contact_number": contact_number
    }
    
    # Convert to pydantic model
    schedule = parse_obj_as(schemas.DoctorScheduleCreate, schedule_data)
    
    # Create schedule
    return crud.create_schedule(db, schedule, image_filename)

@router.put("/{schedule_id}", response_model=schemas.DoctorScheduleResponse)
async def update_schedule(
    schedule_id: int,
    name: Optional[str] = Form(None),
    specialization: Optional[str] = Form(None),
    day_of_week: Optional[str] = Form(None),
    start_time: Optional[str] = Form(None),
    end_time: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(None),
    specific_date: Optional[str] = Form(None),
    contact_number: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Update doctor schedule with optional image
    """
    # Handle image upload if provided
    image_filename = None
    if image and image.filename:
        # Save the uploaded file
        file_extension = os.path.splitext(image.filename)[1]
        image_filename = f"{name or 'doctor'}_{os.urandom(4).hex()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, image_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    
    # Create update data
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if specialization is not None:
        update_data["specialization"] = specialization
    if day_of_week is not None:
        update_data["day_of_week"] = day_of_week
    if start_time is not None:
        update_data["start_time"] = time.fromisoformat(start_time)
    if end_time is not None:
        update_data["end_time"] = time.fromisoformat(end_time)
    if is_available is not None:
        update_data["is_available"] = is_available
    if specific_date is not None:
        update_data["specific_date"] = date.fromisoformat(specific_date) if specific_date else None
    if contact_number is not None:
        update_data["contact_number"] = contact_number
    
    # Convert to pydantic model
    schedule_update = parse_obj_as(schemas.DoctorScheduleUpdate, update_data)
    
    # Update schedule
    updated_schedule = crud.update_schedule(db, schedule_id, schedule_update, image_filename)
    if not updated_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated_schedule

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """
    Delete a doctor schedule
    """
    result = crud.delete_schedule(db, schedule_id)
    if not result:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return None