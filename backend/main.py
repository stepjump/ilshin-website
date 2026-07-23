import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI(
    title="Ilshin Website API",
    description="Render & Neon DB 연동 API 서비스",
    version="1.0.0"
)

# 1. Neon DB 연결 URL 설정 (Render 환경변수 DATABASE_URL 읽기)
# postgres:// 로 시작하면 SQLAlchemy 호환을 위해 postgresql:// 로 자동 변환
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2. SQLAlchemy 엔진 및 세션 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Company DB 모델 정의 (Neon DB의 company_info 테이블과 매핑)
class Company(Base):
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slogan = Column(String)
    about = Column(Text)

# DB에 테이블이 없을 경우 자동으로 생성
Base.metadata.create_all(bind=engine)

# 4. DB 세션 의존성 (Dependency) 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. 루트 엔드포인트 (https://ilshin-website.onrender.com/ 접속 시)
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to Ilshin Website API Server",
        "endpoints": {
            "company_info": "/api/company",
            "swagger_docs": "/docs"
        }
    }

# 6. /api/company 엔드포인트
@app.get("/api/company")
def get_company(db: Session = Depends(get_db)):
    company_data = db.query(Company).first()
    if not company_data:
        raise HTTPException(status_code=404, detail="Company information not found")
    return company_data