import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI()

# 1. Neon DB 연결 URL 설정 (Render 환경변수 DATABASE_URL 읽기)
# postgres:// 로 시작하면 SQLAlchemy 호환을 위해 postgresql:// 로 자동 변환
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2. SQLAlchemy 엔진 및 세션 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Company DB 모델 정의
class Company(Base):
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slogan = Column(String)
    about = Column(Text)

# 4. DB 세션 의존성 (Dependency) 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. /api/company 엔드포인트 (db: Session = Depends(get_db) 필수!)
@app.get("/api/company")
def get_company(db: Session = Depends(get_db)):
    company_data = db.query(Company).first()
    if not company_data:
        raise HTTPException(status_code=404, detail="Company information not found")
    return company_data