from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db
from typing import List

router = APIRouter(prefix="/visits", tags=["Visits"])

@router.get("/{doctor_id}", response_model=List[schemas.VisitResponse])
def get_visits(doctor_id: int, db: Session = Depends(get_db)):
    """Get all visits for a specific doctor"""
    try:
        print(f"Fetching visits for doctor_id: {doctor_id}")
        visits = crud.get_visits(db, doctor_id)
        if not visits:
            return []
        return visits
    except Exception as e:
        print(f"Error in get_visits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detail/{visit_id}", response_model=schemas.VisitResponse)
def get_visit_detail(visit_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific visit"""
    visit = crud.get_visit(db, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.post("/{doctor_id}", response_model=schemas.VisitResponse, status_code=status.HTTP_201_CREATED)
def create_visit(doctor_id: int, visit: schemas.VisitCreate, db: Session = Depends(get_db)):
    """Create a new visit for a doctor"""
    return crud.create_visit(db, visit, doctor_id)

@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_visit(visit_id: int, db: Session = Depends(get_db)):
    """Delete a visit and all associated patients"""
    result = crud.delete_visit(db, visit_id)
    if not result:
        raise HTTPException(status_code=404, detail="Visit not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)