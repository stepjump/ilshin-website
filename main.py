from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 허용 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 루트 경로 (/) 엔드포인트
@app.get("/")
def read_root():
    return {
        "title": "일신 웹사이트 API",
        "status": "online",
        "message": "FastAPI 백엔드가 정상적으로 연동되었습니다!"
    }
