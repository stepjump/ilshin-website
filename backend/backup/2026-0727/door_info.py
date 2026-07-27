from datetime import datetime
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, Integer, Text, String, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator

try:
    from .main import Base, get_db
except ImportError:
    from main import Base, get_db

router = APIRouter(
    prefix="/api/door-info",
    tags=["Door Info Management"]
)


# 1. DB 모델 (DB의 실제 ver 컬럼 타입인 Integer/String 모두 수용되도록 유연화)
class DoorInfo(Base):
    __tablename__ = "door_info"

    id = Column(Integer, primary_key=True, index=True)
    info = Column(Text, nullable=False)
    ver = Column(String(50), nullable=True)  # nullable=True로 세팅하여 파싱 예외 방지
    useyn = Column(String(1), default="Y")
    created_at = Column(DateTime, default=datetime.utcnow)


# 2. Pydantic 스키마 (어떤 형태의 ver 값이 들어와도 문자열로 자동 변환)
class DoorInfoBase(BaseModel):
    info: str
    ver: Optional[Any] = None  # int, str 모두 받을 수 있도록 Any 처리
    useyn: Optional[str] = "Y"

    @field_validator('ver', mode='before')
    @classmethod
    def convert_ver_to_str(cls, v):
        if v is None:
            return ""
        return str(v)

class DoorInfoCreate(DoorInfoBase):
    pass

class DoorInfoUpdate(BaseModel):
    info: Optional[str] = None
    ver: Optional[Any] = None
    useyn: Optional[str] = None

class DoorInfoResponse(DoorInfoBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 3. CRUD API (CORS 리다이렉트 방지를 위해 ""와 "/" 둘 다 등록)
@router.get("", response_model=List[DoorInfoResponse])
@router.get("/", response_model=List[DoorInfoResponse])
def get_all_door_info(db: Session = Depends(get_db)):
    try:
        return db.query(DoorInfo).order_by(DoorInfo.id.desc()).all()
    except Exception as e:
        print(f"door-info 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/active", response_model=DoorInfoResponse)
def get_active_door_info(db: Session = Depends(get_db)):
    active_item = db.query(DoorInfo).filter(DoorInfo.useyn == "Y").order_by(DoorInfo.id.desc()).first()
    if not active_item:
        raise HTTPException(status_code=404, detail="활성화된 첫화면 정보를 찾을 수 없습니다.")
    return active_item


@router.post("", response_model=DoorInfoResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=DoorInfoResponse, status_code=status.HTTP_201_CREATED)
def create_door_info(item: DoorInfoCreate, db: Session = Depends(get_db)):
    item_dict = item.model_dump()
    if item_dict.get("ver") is not None:
        item_dict["ver"] = str(item_dict["ver"])
        
    db_item = DoorInfo(**item_dict)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


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
    if "ver" in update_dict and update_dict["ver"] is not None:
        update_dict["ver"] = str(update_dict["ver"])

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