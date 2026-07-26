from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, Integer, Text, String, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel

try:
    from .main import Base, get_db
except ImportError:
    from main import Base, get_db

router = APIRouter(
    prefix="/api/door-info",
    tags=["Door Info Management"]
)


class DoorInfo(Base):
    __tablename__ = "door_info"

    id = Column(Integer, primary_key=True, index=True)
    info = Column(Text, nullable=False)
    ver = Column(Integer, nullable=False)
    useyn = Column(String(1), default="Y")
    created_at = Column(DateTime, default=datetime.utcnow)


class DoorInfoBase(BaseModel):
    info: str
    ver: int
    useyn: Optional[str] = "Y"

class DoorInfoCreate(DoorInfoBase):
    pass

class DoorInfoUpdate(BaseModel):
    info: Optional[str] = None
    ver: Optional[int] = None
    useyn: Optional[str] = None

class DoorInfoResponse(DoorInfoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=DoorInfoResponse, status_code=status.HTTP_201_CREATED)
def create_door_info(item: DoorInfoCreate, db: Session = Depends(get_db)):
    db_item = DoorInfo(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/active", response_model=DoorInfoResponse)
def get_active_door_info(db: Session = Depends(get_db)):
    active_item = db.query(DoorInfo).filter(DoorInfo.useyn == "Y").order_by(DoorInfo.id.desc()).first()
    if not active_item:
        raise HTTPException(status_code=404, detail="활성화된 첫화면 정보를 찾을 수 없습니다.")
    return active_item


@router.get("/", response_model=List[DoorInfoResponse])
def get_all_door_info(db: Session = Depends(get_db)):
    return db.query(DoorInfo).order_by(DoorInfo.id.desc()).all()


@router.get("/{info_id}", response_model=DoorInfoResponse)
def get_door_info(info_id: int, db: Session = Depends(get_db)):
    item = db.query(DoorInfo).filter(DoorInfo.id == info_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    return item


@router.put("/{info_id}", response_model=DoorInfoResponse)
def update_door_info(info_id: int, update_data: DoorInfoUpdate, db: Session = Depends(get_db)):
    item = db.query(DoorInfo).filter(DoorInfo.id == info_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{info_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_door_info(info_id: int, db: Session = Depends(get_db)):
    item = db.query(DoorInfo).filter(DoorInfo.id == info_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    
    db.delete(item)
    db.commit()
    return None