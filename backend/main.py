from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (Vercel 프론트엔드 연동 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 주소 접속 테스트
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "일신 백엔드 API 서버가 성공적으로 작동 중입니다!"
    }


# 회사 정보 API
@app.get("/api/company")
# def get_company_info():
#     return {
#         "name": "(주)일신",
#         "slogan": "신뢰와 기술로 미래를 열어가는 기업",
#         "about": "일신은 최고 품질의 서비스와 차별화된 기술력으로 고객 가치를 창출합니다.",
#         "services": [
#             {"id": 1, "title": "시스템 통합(SI)", "desc": "고객 맞춤형 IT 인프라 및 시스템 구축"},
#             {"id": 2, "title": "소프트웨어 개발", "desc": "웹, 모바일, AI 솔루션 전문 개발"},
#             {"id": 3, "title": "컨설팅 서비스", "desc": "디지털 전환을 위한 전문 컨설팅 제공"}
#         ]
#     }
def get_company():
    # DB에서 데이터를 SELECT 해서 가져와야 함
    company_data = db.query(Company).first()
    return company_data
