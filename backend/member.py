from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import jwt  # PyJWT 패키지 (pip install pyjwt 필요)

# ----------------------------------------------------
# 0. 경로 예외 처리를 통한 임포트 (Import Error 방지)
# ----------------------------------------------------
try:
    from .main import Base, get_db
except ImportError:
    from main import Base, get_db

# JWT 인증 환경설정
SECRET_KEY = "ilshin_website_secret_key_change_me"  # 보안용 비밀키
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 토큰 유효기간 (24시간)

# OAuth2 패스워드 폼 설정 (Swagger 상단 Authorize 버튼과 연동)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/members/login", auto_error=False)


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


# U (Update) - 회원정보 수정용
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


# Token Response - 로그인 토큰 응답용
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    name: str
    role: str


# ==========================================
# 3. Router 인스턴스 & 토큰 유틸리티
# ==========================================
router = APIRouter(
    prefix="/api/members",
    tags=["Member Management"]
)

# JWT 액세스 토큰 생성 함수
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 현재 로그인한 사용자 정보 추출 (다른 모듈에서 의존성 주입용으로 사용)
def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[Member]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except Exception:
        return None

    user = db.query(Member).filter(Member.email == email).first()
    return user


# ==========================================
# 4. 로그인 및 CRUD API 엔드포인트
# ==========================================

# [Auth] 로그인 및 JWT 토큰 발급
@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Swagger Authorize 폼에서는 username 필드에 email이 전달됩니다.
    user = db.query(Member).filter(Member.email == form_data.username).first()
    
    if not user or user.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 계정입니다."
        )

    # 토큰 발급 (email을 sub 값으로 저장)
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email,
        "name": user.name,
        "role": user.role
    }


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


# [C - Create] 신규 회원 등록 (회원가입)
@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
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