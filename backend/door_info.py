from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, Integer, Text, String, DateTime, func
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


# 1. DB 모델 (ver 컬럼을 Integer 타입으로 설정)
class DoorInfo(Base):
    __tablename__ = "door_info"

    id = Column(Integer, primary_key=True, index=True)
    info = Column(Text, nullable=False)
    ver = Column(Integer, nullable=False, default=1)  # ★ Integer 타입 지정
    useyn = Column(String(1), default="Y")
    created_at = Column(DateTime, default=datetime.utcnow)


# 2. Pydantic 스키마 (ver를 int 타입으로 설정)
class DoorInfoBase(BaseModel):
    info: str
    ver: Optional[int] = None  # 생성 시 자동 계산을 위해 Optional 처리
    useyn: Optional[str] = "Y"

class DoorInfoCreate(DoorInfoBase):
    pass

class DoorInfoUpdate(BaseModel):
    info: Optional[str] = None
    ver: Optional[int] = None
    useyn: Optional[str] = None

class DoorInfoResponse(BaseModel):
    id: int
    info: str
    ver: int  # ★ 정수형으로 응답
    useyn: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 3. CRUD API

# 신규 레코드 생성 (ver 미입력 시 기존 MAX(ver) + 1 로 자동 증가)
@router.post("", response_model=DoorInfoResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=DoorInfoResponse, status_code=status.HTTP_201_CREATED)
def create_door_info(item: DoorInfoCreate, db: Session = Depends(get_db)):
    try:
        item_dict = item.model_dump()
        
        # ver 입력값이 없으면 현재 DB의 최고 ver + 1 처리
        if item_dict.get("ver") is None:
            max_ver = db.query(func.max(DoorInfo.ver)).scalar()
            item_dict["ver"] = (max_ver + 1) if max_ver is not None else 1

        db_item = DoorInfo(**item_dict)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        print(f"door-info 생성 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 생성 중 오류가 발생했습니다: {str(e)}"
        )


# 전체 목록 조회
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


# 활성화된 첫 화면 정보 조회 (/api/door-info/active)
@router.get("/active", response_model=DoorInfoResponse)
def get_active_door_info(db: Session = Depends(get_db)):
    active_item = db.query(DoorInfo).filter(DoorInfo.useyn == "Y").order_by(DoorInfo.id.desc()).first()
    if not active_item:
        raise HTTPException(status_code=404, detail="활성화된 첫화면 정보를 찾을 수 없습니다.")
    return active_item


# 단일 항목 조회
@router.get("/{info_id}", response_model=DoorInfoResponse)
def get_door_info(info_id: int, db: Session = Depends(get_db)):
    item = db.query(DoorInfo).filter(DoorInfo.id == info_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    return item


# 항목 수정
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


# 항목 삭제
@router.delete("/{info_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_door_info(info_id: int, db: Session = Depends(get_db)):
    item = db.query(DoorInfo).filter(DoorInfo.id == info_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    
    db.delete(item)
    db.commit()
    return None