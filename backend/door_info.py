from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, Integer, Text, String, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# main.py에서 정의한 Base와 get_db 불러오기
from main import Base, get_db

# 라우터 생성
router = APIRouter(
    prefix="/api/door-info",
    tags=["Door Info Management"]
)

# ==========================================
# 1. SQLAlchemy 데이터베이스 모델
# ==========================================
class DoorInfo(Base):
    __tablename__ = "door_info"

    id = Column(Integer, primary_key=True, index=True)
    info = Column(Text, nullable=False)
    ver = Column(Integer, nullable=False)  # <-- String(20)에서 Integer로 변경!
    useyn = Column(String(1), default="Y")
    created_at = Column(DateTime, default=datetime.utcnow)

# 2. Pydantic 스키마 수정
class DoorInfoBase(BaseModel):
    info: str
    ver: int  # <-- str에서 int로 변경! (예: 1, 2, 3...)
    useyn: Optional[str] = "Y"

class DoorInfoUpdate(BaseModel):
    info: Optional[str] = None
    ver: Optional[int] = None  # <-- int로 변경
    useyn: Optional[str] = None
    
# ==========================================
# 2. Pydantic 검증 스키마
# ==========================================
class DoorInfoBase(BaseModel):
    info: str
    ver: str
    useyn: Optional[str] = "Y"

class DoorInfoCreate(DoorInfoBase):
    pass

class DoorInfoUpdate(BaseModel):
    info: Optional[str] = None
    ver: Optional[str] = None
    useyn: Optional[str] = None

class DoorInfoResponse(DoorInfoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# 3. CRUD API 엔드포인트
# ==========================================

# [CREATE] 첫화면 정보 등록
@router.post("/", response_model=DoorInfoResponse, status_code=status.HTTP_201_CREATED)
def create_door_info(item: DoorInfoCreate, db: Session = Depends(get_db)):
    db_item = DoorInfo(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# [READ - Active] 현재 웹사이트용 활성화된(useyn='Y') 최신 첫화면 정보 조회
@router.get("/active", response_model=DoorInfoResponse)
def get_active_door_info(db: Session = Depends(get_db)):
    active_item = db.query(DoorInfo).filter(DoorInfo.useyn == "Y").order_by(DoorInfo.id.desc()).first()
    if not active_item:
        raise HTTPException(status_code=404, detail="활성화된 첫화면 정보를 찾을 수 없습니다.")
    return active_item

# [READ - All] 목록 전체 조회 (관리자용)
@router.get("/", response_model=List[DoorInfoResponse])
def get_all_door_info(db: Session = Depends(get_db)):
    return db.query(DoorInfo).order_by(DoorInfo.id.desc()).all()

# [READ - Single] 특정 ID 조회
@router.get("/{info_id}", response_model=DoorInfoResponse)
def get_door_info(info_id: int, db: Session = Depends(get_db)):
    item = db.query(DoorInfo).filter(DoorInfo.id == info_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    return item

# [UPDATE] 정보 수정
@router.put("/{info_id}", response_model=DoorInfoResponse)
def update_door_info(info_id: int, update_data: DoorInfoUpdate, db: Session = Depends(get_db)):
    item = db.query(DoorInfo).filter(DoorInfo.id == info_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return item

# [DELETE] 삭제
@router.delete("/{info_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_door_info(info_id: int, db: Session = Depends(get_db)):
    item = db.query(DoorInfo).filter(DoorInfo.id == info_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    
    db.delete(item)
    db.commit()
    return None

