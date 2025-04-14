from pydantic import BaseModel, Field
from datetime import date, time,datetime
from typing import List, Optional
 


# Doctor Schema
class DoctorBase(BaseModel):
    name: str
    specialization: str
    phone: str

class DoctorCreate(DoctorBase):
    # Image will be handled separately in the file upload
    pass

class DoctorResponse(DoctorBase):
    id: int
    image_filename: Optional[str] = None
    
    class Config:
        from_attributes = True

# Visit Schema
class VisitBase(BaseModel):
    date: date

class VisitCreate(VisitBase):
    pass

class VisitResponse(VisitBase):
    id: int
    doctor_id: int
    totalPatients: Optional[int] = 0
    
    class Config:
        from_attributes = True

# Patient Schema
class PatientBase(BaseModel):
    name: str
    contact: str
    fee_status: str = Field(default="due")

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    visit_id: int
    serial_no: int
    
    class Config:
        from_attributes = True
        populate_by_name = True


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    fee_status: Optional[str] = None

# Unique Patient Schema
class UniquePatientResponse(BaseModel):
    id: int
    name: str
    contact: str
    fee_status: str
    doctor_visits: List[int]
    
    class Config:
        from_attributes = True

# Doctor Schedule Schema
# schemas.py
class DoctorScheduleBase(BaseModel):
    name: str
    specialization: str
    day_of_week: str
    start_time: time
    end_time: time
    is_available: bool = True
    specific_date: Optional[date] = None
    contact_number: Optional[str] = None

class DoctorScheduleCreate(DoctorScheduleBase):
    pass

class DoctorScheduleUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    day_of_week: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None
    specific_date: Optional[date] = None
    contact_number: Optional[str] = None

class DoctorScheduleResponse(DoctorScheduleBase):
    id: int
    image_filename: Optional[str] = None
    
    class Config:
        from_attributes = True
    

class DoctorWithScheduleResponse(DoctorResponse):
    schedules: List[DoctorScheduleResponse] = []

# Gallery Image schemas
class GalleryImageBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: str
    order_index: int = 0
    is_active: bool = True

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImageUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None

class GalleryImageResponse(GalleryImageBase):
    id: int
    
    class Config:
        from_attributes = True

       

