from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel

# ----------------------------------------------------
# 0. 경로 예외 처리를 통한 임포트 (Import Error 방지)
# ----------------------------------------------------
try:
    from .main import Base, get_db
    from .member import Member
except ImportError:
    from main import Base, get_db
    from member import Member

# 토큰 추출을 위한 OAuth2 설정 (비회원/회원 겸용 처리용)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)


# ==========================================
# 1. DB 모델 정의 (Member 연동)
# ==========================================
class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, index=True)
    board_type = Column(String(50), nullable=False, default="free", index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(255), nullable=True)  # 비회원 글용 비밀번호 (회원은 선택)

    # member 테이블과의 외래키(FK) 및 관계 설정
    member_id = Column(Integer, ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    author = Column(String(50), default="익명")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Member 모델 매핑 (member.py의 Member 클래스와 역참조 연결)
    member = relationship("Member", backref="boards")


# ==========================================
# 2. Pydantic 스키마 정의
# ==========================================
class BoardBase(BaseModel):
    title: str
    content: str
    author: Optional[str] = "익명"


# C (Create) - 작성 스키마
class BoardCreate(BoardBase):
    password: Optional[str] = None  # 비회원은 필수 입력, 회원은 자동 처리 가능
    member_id: Optional[int] = None


# U (Update) - 수정 스키마
class BoardUpdate(BaseModel):
    password: Optional[str] = None  # 비회원 글 수정 시 필요
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None


# D (Delete) - 삭제 요청 스키마
class BoardDeleteRequest(BaseModel):
    password: Optional[str] = None


# R (Response) - 응답 스키마
class BoardResponse(BoardBase):
    id: int
    board_type: str
    member_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# 3. Router 인스턴스 및 로그인 정보 헬퍼
# ==========================================
router = APIRouter(
    prefix="/api/board",
    tags=["Multi-Board Management"]
)

# 로그인 상태(토큰) 확인 헬퍼 함수
def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[Member]:
    if not token:
        return None
    try:
        # member.py 내에 토큰 검증 로직이 있거나, 간단히 DB 조회로 연결
        # JWT 파싱 및 유저 조회 로직 구현 가능
        import jwt
        SECRET_KEY = "YOUR_SECRET_KEY"  # member.py의 SECRET_KEY와 동일하게 설정
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email:
            return db.query(Member).filter(Member.email == email).first()
    except Exception:
        return None
    return None


# ==========================================
# 4. CRUD API 엔드포인트
# ==========================================

# [R - Read All] 특정 게시판 목록 조회
@router.get("/{board_type}", response_model=List[BoardResponse])
def get_boards_by_type(board_type: str, db: Session = Depends(get_db)):
    boards = db.query(Board).filter(Board.board_type == board_type).order_by(Board.id.desc()).all()
    return boards


# [R - Read One] 특정 게시글 단건 조회
@router.get("/{board_type}/{board_id}", response_model=BoardResponse)
def get_board_by_id(board_type: str, board_id: int, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )
    return board


# [C - Create] 게시글 작성 (회원/비회원 유연하게 처리)
@router.post("/{board_type}", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    board_type: str, 
    board: BoardCreate, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user_optional)
):
    board_data = board.model_dump()

    # 1. 로그인한 회원인 경우: member 테이블 정보(email, name, role) 연동
    if current_user:
        board_data["member_id"] = current_user.id
        board_data["author"] = current_user.name  # member 테이블의 name 반영
    
    # 2. 직접 member_id가 전달된 경우 (관리자 등록 등 예외 케이스)
    elif board.member_id:
        existing_member = db.query(Member).filter(Member.id == board.member_id).first()
        if not existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않는 회원 ID(member_id)입니다."
            )
        board_data["author"] = existing_member.name

    # 3. 비회원인 경우: 비밀번호 입력 여부 검증
    else:
        if not board.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비회원 게시글 작성 시 비밀번호 입력은 필수입니다."
            )

    db_board = Board(
        board_type=board_type,
        **board_data
    )
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


# [U - Update] 게시글 수정
@router.put("/{board_type}/{board_id}", response_model=BoardResponse)
def update_board(
    board_type: str, 
    board_id: int, 
    board_data: BoardUpdate, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user_optional)
):
    db_board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not db_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 수정 권한 검증 (로그인한 글 작성자 본인이거나, 비밀번호가 일치하는 경우)
    is_author = current_user and current_user.id == db_board.member_id
    is_password_correct = board_data.password and db_board.password == board_data.password

    if not (is_author or is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="수정 권한이 없습니다. 비밀번호를 확인해 주세요."
        )

    # 업데이트 적용
    update_dict = board_data.model_dump(exclude_unset=True, exclude={"password"})
    for key, value in update_dict.items():
        setattr(db_board, key, value)

    db.commit()
    db.refresh(db_board)
    return db_board


# [D - Delete] 게시글 삭제
@router.post("/{board_type}/{board_id}/delete", status_code=status.HTTP_200_OK)
def delete_board(
    board_type: str, 
    board_id: int, 
    delete_req: BoardDeleteRequest, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user_optional)
):
    db_board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not db_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 삭제 권한 검증 (본인 작성 글 또는 비밀번호 일치)
    is_author = current_user and current_user.id == db_board.member_id
    is_password_correct = delete_req.password and db_board.password == delete_req.password

    if not (is_author or is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="삭제 권한이 없습니다. 비밀번호를 확인해 주세요."
        )

    db.delete(db_board)
    db.commit()
    return {"message": f"게시글(ID: {board_id})이 성공적으로 삭제되었습니다."}

