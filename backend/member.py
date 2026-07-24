from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

# main.py에서 생성한 Base, get_db를 가져옵니다.
# (파일 구조에 따라 import 경로를 맞춰주세요)
from main import Base, get_db


# ==========================================
# 1. DB 모델 정의 (member 테이블 매핑)
# ==========================================
class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================
# 2. Pydantic 스키마 정의 (검증용)
# ==========================================
class MemberBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    role: Optional[str] = "user"
    is_active: Optional[bool] = True


# C (Create) - 회원가입/등록용
class MemberCreate(MemberBase):
    password: str


# U (Update) - 회원정보 수정용 (선택적 변경)
class MemberUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# R (Response) - 회원정보 응답용 (비밀번호 제외)
class MemberResponse(MemberBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# 3. Router 인스턴스 생성
# ==========================================
router = APIRouter(
    prefix="/api/members",
    tags=["Member Management"]
)


# ==========================================
# 4. CRUD API 엔드포인트
# ==========================================

# [R - Read All] 전체 회원 목록 조회
@router.get("", response_model=List[MemberResponse])
def get_all_members(db: Session = Depends(get_db)):
    members = db.query(Member).all()
    return members


# [R - Read One] 특정 ID 회원 단건 조회
@router.get("/{member_id}", response_model=MemberResponse)
def get_member_by_id(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Member not found"
        )
    return member


# [C - Create] 신규 회원 등록
@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    existing_member = db.query(Member).filter(Member.email == member.email).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )

    db_member = Member(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


# [U - Update] 특정 ID 회원 정보 수정
@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member_data: MemberUpdate, db: Session = Depends(get_db)):
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Member not found"
        )

    # 이메일을 수정하려 할 때 다른 회원과 중복 여부 확인
    if member_data.email and member_data.email != db_member.email:
        email_check = db.query(Member).filter(Member.email == member_data.email).first()
        if email_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already in use by another member"
            )

    update_data = member_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_member, key, value)

    db.commit()
    db.refresh(db_member)
    return db_member


# [D - Delete] 특정 ID 회원 삭제
@router.delete("/{member_id}", status_code=status.HTTP_200_OK)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Member not found"
        )

    db.delete(db_member)
    db.commit()
    return {"message": f"Member ID {member_id} has been deleted successfully"}
