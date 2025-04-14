from sqlalchemy.orm import Session
import models, schemas
from typing import  Optional
from datetime import date


# CRUD Operations for Doctors
def get_doctors(db: Session):
    return db.query(models.Doctor).all()


def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def create_doctor(db: Session, doctor: schemas.DoctorCreate, image_filename: Optional[str] = None):
    """Create a new doctor with optional image file"""
    # Convert Pydantic model to dict
    doctor_data = doctor.dict()
    
    # Add image filename if provided
    if image_filename:
        doctor_data["image_filename"] = image_filename
    
    db_doctor = models.Doctor(**doctor_data)
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def update_doctor(db: Session, doctor_id: int, doctor: schemas.DoctorCreate, image_filename: Optional[str] = None):
    """Update a doctor with optional image file"""
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not db_doctor:
        return None
    
    # Update doctor data
    for key, value in doctor.dict().items():
        setattr(db_doctor, key, value)
    
    # Update image filename if provided
    if image_filename is not None:
        setattr(db_doctor, "image_filename", image_filename)
    
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def delete_doctor(db: Session, doctor_id: int):
    # First delete all related visits and their patients
    visits = db.query(models.Visit).filter(models.Visit.doctor_id == doctor_id).all()
    for visit in visits:
        delete_visit(db, visit.id)
    
    # Then delete the doctor
    result = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).delete()
    db.commit()
    return result > 0


# CRUD Operations for Visits
def get_visits(db: Session, doctor_id: int):
    visits = db.query(models.Visit).filter(models.Visit.doctor_id == doctor_id).all()
    
    # Add totalPatients count to each visit
    for visit in visits:
        setattr(visit, "totalPatients", len(visit.patients))
    
    return visits


def get_visit(db: Session, visit_id: int):
    visit = db.query(models.Visit).filter(models.Visit.id == visit_id).first()
    if visit:
        setattr(visit, "totalPatients", len(visit.patients))
    return visit


def create_visit(db: Session, visit: schemas.VisitCreate, doctor_id: int):
    db_visit = models.Visit(**visit.dict(), doctor_id=doctor_id)
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    # Add totalPatients for response
    setattr(db_visit, "totalPatients", 0)
    return db_visit


def delete_visit(db: Session, visit_id: int):
    # First, delete associated patients
    db.query(models.Patient).filter(models.Patient.visit_id == visit_id).delete()
    
    # Then delete the visit
    result = db.query(models.Visit).filter(models.Visit.id == visit_id).delete()
    db.commit()
    return result > 0


# CRUD Operations for Patients
def get_all_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()


def get_patients(db: Session, visit_id: int):
    try:
        patients = db.query(models.Patient).filter(models.Patient.visit_id == visit_id).all()
        return patients
    except Exception as e:
        print(f"Database error getting patients: {str(e)}")
        raise


def create_patient(db: Session, patient: schemas.PatientCreate, visit_id: int, serial_no: int):
    db_patient = models.Patient(**patient.dict(), visit_id=visit_id, serial_no=serial_no)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def toggle_patient_fee_status(db: Session, patient_id: int):
    """
    Toggle the fee status of a patient between 'paid' and 'due'
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        return None
    
    # Toggle the fee status
    patient.fee_status = "paid" if patient.fee_status == "due" else "due"
    db.commit()
    db.refresh(patient)
    return patient
def update_patient(db: Session, patient_id: int, patient_update: schemas.PatientUpdate):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        return None
    
    update_data = patient_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient_id: int):
    """
    Delete a patient by ID
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        return False
    
    db.delete(patient)
    db.commit()
    return True


def get_unique_patients(db: Session):
    """
    Get all unique patients with information about which doctors they've visited.
    A patient is considered unique based on their name and contact information.
    """
    # Get all patients
    all_patients = get_all_patients(db)
    
    # Create a dictionary to store unique patients
    unique_patients_dict = {}
    
    for patient in all_patients:
        # Create a unique key based on name and contact
        key = f"{patient.name}-{patient.contact}"
        
        # Get the associated visit
        visit = get_visit(db, patient.visit_id)
        
        if visit:
            doctor_id = visit.doctor_id
            
            if key not in unique_patients_dict:
                # First time seeing this patient
                unique_patients_dict[key] = {
                    "id": patient.id,
                    "name": patient.name,
                    "contact": patient.contact,
                    "fee_status": patient.fee_status,
                    "doctor_visits": set([doctor_id])
                }
            else:
                # We've seen this patient before, just add the doctor
                unique_patients_dict[key]["doctor_visits"].add(doctor_id)
    
    # Convert sets to lists for JSON serialization
    for patient in unique_patients_dict.values():
        patient["doctor_visits"] = list(patient["doctor_visits"])
    
    return list(unique_patients_dict.values())


# CRUD Operations for Doctor Schedules
def get_schedules(db: Session, skip: int = 0, limit: int = 100):
    """Get all doctor schedules"""
    return db.query(models.DoctorSchedule).offset(skip).limit(limit).all()

def create_schedule(db: Session, schedule: schemas.DoctorScheduleCreate, image_filename: Optional[str] = None):
    """Create a new doctor schedule with optional image file"""
    schedule_data = schedule.dict()
    
    # Add image filename if provided
    if image_filename:
        schedule_data["image_filename"] = image_filename
    
    db_schedule = models.DoctorSchedule(**schedule_data)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_schedule(db: Session, schedule_id: int, schedule: schemas.DoctorScheduleUpdate, image_filename: Optional[str] = None):
    """Update a doctor schedule with optional image file"""
    db_schedule = db.query(models.DoctorSchedule).filter(models.DoctorSchedule.id == schedule_id).first()
    if not db_schedule:
        return None
    
    # Update schedule data
    update_data = schedule.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    # Update image filename if provided
    if image_filename is not None:
        setattr(db_schedule, "image_filename", image_filename)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: int):
    result = db.query(models.DoctorSchedule).filter(models.DoctorSchedule.id == schedule_id).delete()
    db.commit()
    return result > 0


# CRUD Operations for Gallery
def get_gallery_images(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True):
    query = db.query(models.GalleryImage)
    if active_only:
        query = query.filter(models.GalleryImage.is_active == True)
    
    # Order by order_index
    query = query.order_by(models.GalleryImage.order_index)
    
    return query.offset(skip).limit(limit).all()


def get_gallery_image(db: Session, image_id: int):
    return db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()


def create_gallery_image(db: Session, image_data):
    db_image = models.GalleryImage(**image_data)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def update_gallery_image(db: Session, image_id: int, image_data):
    db_image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if not db_image:
        return None
    
    for key, value in image_data.items():
        setattr(db_image, key, value)
    
    db.commit()
    db.refresh(db_image)
    return db_image


def delete_gallery_image(db: Session, image_id: int):
    db_image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if not db_image:
        return None
    
    db.delete(db_image)
    db.commit()
    return db_image