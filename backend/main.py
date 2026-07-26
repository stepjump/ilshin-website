import os
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

# 1. OAuth2 패스워드 스킴 설정
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/members/login",
    auto_error=False
)

# .env 파일 환경변수 로드
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")

app = FastAPI(
    title="Ilshin Website API",
    description="Render & Neon DB 연동 API 서비스",
    version="1.0.0"
)

# 2. CORS 설정 (보안 강화: '*' 제거 및 실제 사용할 도메인 명시)
origins = [
    "https://ilshin-website-theta.vercel.app",
    "https://vercel.com",
    "http://localhost:3000",
    "http://localhost:5173",  # Vue 3 (Vite 기본 포트)
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Neon DB 연결 URL 설정 (postgresql:// 호환 변환)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy 엔진 생성 (SSL 자동 재연결 및 커넥션 풀 옵션 추가)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # 쿼리 실행 전 DB 연결 상태 자동 점검 (끊겼으면 재연결)
    pool_recycle=300,         # 5분(300초)마다 커넥션 자동 갱신
    pool_size=5,              # 커넥션 풀 크기
    max_overflow=10           # 최대 오버플로우 커넥션
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


# 4. 회사 정보 DB 모델
class Company(Base):
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    slogan = Column(String(255), nullable=True)
    about = Column(Text, nullable=True)


Base.metadata.create_all(bind=engine)


# 5. Pydantic 검증 스키마
class CompanyBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    slogan: Optional[str] = None
    about: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    slogan: Optional[str] = None
    about: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 6. DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 7. 기본 메인 페이지
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to Ilshin Website API Server",
        "endpoints": {
            "company_list": "/api/company",
            "swagger_docs": "/docs"
        }
    }


# 8. Company CRUD API
@app.get("/api/company", response_model=List[CompanyResponse])
def get_all_company_info(db: Session = Depends(get_db)):
    return db.query(Company).all()


@app.get("/api/company/{company_id}", response_model=CompanyResponse)
def get_company_by_id(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company information not found")
    return company


@app.post("/api/company", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company_info(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@app.put("/api/company/{company_id}", response_model=CompanyResponse)
def update_company_info(company_id: int, company_data: CompanyUpdate, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company information not found")

    update_data = company_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company


@app.delete("/api/company/{company_id}", status_code=status.HTTP_200_OK)
def delete_company_info(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company information not found")

    db.delete(db_company)
    db.commit()
    return {"message": f"Company ID {company_id} has been deleted successfully"}


# 9. 서브 라우터 등록
try:
    from . import member, door_info, board
except ImportError:
    import member
    import door_info
    import board

app.include_router(member.router)
app.include_router(door_info.router)
app.include_router(board.router)