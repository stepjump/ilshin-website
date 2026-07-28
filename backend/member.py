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

try:
    from .main import Base, get_db
except ImportError:
    from main import Base, get_db

# 환경변수에서 Secret Key를 읽어오며, 없는 경우 기본값 사용
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ilshin_website_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/members/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력받은 비밀번호와 DB의 해시 비밀번호 일치 여부 확인 (bcrypt 순수 사용)"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"비밀번호 검증 오류: {e}")
        return False


def get_password_hash(password: str) -> str:
    """비밀번호 Bcrypt 암호화"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# 1. DB 모델 정의
class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(20), default="user")
    is_active = Column(String(1), default="Y", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 2. Pydantic 스키마 정의
class MemberBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    role: Optional[str] = "user"
    is_active: Optional[str] = "Y"


class MemberCreate(MemberBase):
    password: str


class MemberUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[str] = None


class MemberResponse(MemberBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    name: str
    phone: Optional[str] = None  # phone 필드 포함
    role: str


# 3. Router 인스턴스
router = APIRouter(
    prefix="/api/members",
    tags=["Member Management"]
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(encoded_jwt, bytes):
        return encoded_jwt.decode('utf-8')
    return str(encoded_jwt)


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
    if user and user.is_active != "Y":
        return None

    return user


# 4. API 엔드포인트
@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    try:
        user = db.query(Member).filter(Member.email == form_data.username).first()
        
        # 암호화 검증 (verify_password 사용)
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.is_active != "Y":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 계정입니다."
            )

        access_token = create_access_token(data={
            "sub": user.email,
            "name": user.name,
            "email": user.email
        })

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "email": user.email,
            "name": user.name,
            "phone": user.phone or "",  # DB의 phone 값 반환
            "role": user.role or "user"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"로그인 예기치 않은 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 내부 오류: {str(e)}"
        )


@router.get("", response_model=List[MemberResponse])
def get_all_members(db: Session = Depends(get_db)):
    return db.query(Member).all()


@router.get("/{email}", response_model=MemberResponse)
def get_member_by_email(email: str, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.email == email).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"이메일 '{email}'에 해당하는 회원을 찾을 수 없습니다."
        )
    return member


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    existing_member = db.query(Member).filter(Member.email == member.email).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="이미 가입된 이메일입니다."
        )

    member_data = member.model_dump()
    member_data["password"] = get_password_hash(member_data["password"])

    db_member = Member(**member_data)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.put("/{email}", response_model=MemberResponse)
def update_member_by_email(email: str, member_data: MemberUpdate, db: Session = Depends(get_db)):
    db_member = db.query(Member).filter(Member.email == email).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"이메일 '{email}'에 해당하는 회원을 찾을 수 없습니다."
        )

    if member_data.email and member_data.email != db_member.email:
        email_check = db.query(Member).filter(Member.email == member_data.email).first()
        if email_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="변경하려는 이메일이 이미 사용 중입니다."
            )

    update_data = member_data.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])

    for key, value in update_data.items():
        setattr(db_member, key, value)

    db.commit()
    db.refresh(db_member)
    return db_member


@router.delete("/{email}", status_code=status.HTTP_200_OK)
def delete_member_by_email(email: str, db: Session = Depends(get_db)):
    db_member = db.query(Member).filter(Member.email == email).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"이메일 '{email}'에 해당하는 회원을 찾을 수 없습니다."
        )

    db.delete(db_member)
    db.commit()
    return {"message": f"이메일 '{email}' 계정이 성공적으로 삭제되었습니다."}