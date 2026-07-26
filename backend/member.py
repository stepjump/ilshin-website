import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import jwt
import bcrypt


# main.py에서 정의한 Base 및 get_db 의존성 불러오기
try:
    from .main import Base, get_db
except ImportError:
    from main import Base, get_db

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "ilshin-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/members/login", auto_error=False)

router = APIRouter(
    prefix="/api/members",
    tags=["members"]
)


# 1. DB 모델 (member 테이블)
class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 2. Pydantic 스키마
class MemberCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class MemberResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[dict] = None


# 3. 비밀번호 암호화 및 검증 함수
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# 4. JWT 토큰 생성 함수 (★ name 포함 처리 추가)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 5. 회원가입 API
@router.post("/register", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def register_member(member_in: MemberCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Member).filter(Member.email == member_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    hashed_pwd = hash_password(member_in.password)
    db_member = Member(
        email=member_in.email,
        password=hashed_pwd,
        name=member_in.name
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


# 6. 로그인 API (OAuth2Form 및 JSON 입력 모두 지원)
@router.post("/login", response_model=Token)
def login_member(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Member).filter(Member.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ★ JWT Token 페이로드에 member 테이블의 name 값을 명시적으로 포함
    token_data = {
        "sub": user.email,
        "email": user.email,
        "name": user.name
    }
    
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }


# 7. 현재 로그인 유저 정보 조회 API
@router.get("/me", response_model=MemberResponse)
def get_current_member(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="인증 토큰이 없습니다.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="토큰 검증에 실패했습니다.")
        
    user = db.query(Member).filter(Member.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user

