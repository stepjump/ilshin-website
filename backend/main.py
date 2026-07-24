import os
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel

# .env 파일의 환경변수를 읽어옵니다.
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 1. FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="Ilshin Website API",
    description="Render & Neon DB 연동 API 서비스",
    version="1.0.0"
)

# CORS 설정
origins = [
    "https://ilshin-website-theta.vercel.app",  # Vercel 배포 주소
    "http://localhost:3000",                   # 로컬 테스트용
    "*"                                         # 모든 도메인 허용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Neon DB 연결 URL 설정 (SQLAlchemy 호환 변환)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy 엔진 및 세션 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 3. SQLAlchemy DB 모델 정의 (company_info 테이블 전체 컬럼 매핑)
class Company(Base):
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    slogan = Column(String(255), nullable=True)
    about = Column(Text, nullable=True)


# DB 테이블 자동 반영
Base.metadata.create_all(bind=engine)


# 4. Pydantic 스키마 정의 (요청/응답 데이터 검증용)
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


# 5. DB 세션 의존성 (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 6. 기본 메인 페이지
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


# ==========================================
# 7. CRUD API 엔드포인트
# ==========================================

# [R - Read All] 회사 정보 목록 전체 조회
@app.get("/api/company", response_model=List[CompanyResponse])
def get_all_company_info(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    return companies


# [R - Read One] 특정 ID의 회사 정보 단건 조회
@app.get("/api/company/{company_id}", response_model=CompanyResponse)
def get_company_by_id(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company information not found")
    return company


# [C - Create] 새로운 회사 정보 등록 (전체 컬럼 저장)
@app.post("/api/company", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company_info(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


# [U - Update] 특정 ID 회사 정보 수정 (전체 컬럼 선택적 수정 가능)
@app.put("/api/company/{company_id}", response_model=CompanyResponse)
def update_company_info(company_id: int, company_data: CompanyUpdate, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company information not found")

    # 전달된 값만 부분 업데이트 (exclude_unset=True)
    update_data = company_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company


# [D - Delete] 특정 ID 회사 정보 삭제
@app.delete("/api/company/{company_id}", status_code=status.HTTP_200_OK)
def delete_company_info(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company information not found")

    db.delete(db_company)
    db.commit()
    return {"message": f"Company ID {company_id} has been deleted successfully"}




# 1. member 라우터 모듈 불러오기
import member

# 2. member 라우터 등록
app.include_router(member.router)