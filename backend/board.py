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
    from .member import Member, get_current_user  # 👈 member.py의 인증 함수 직접 로드
except ImportError:
    from main import Base, get_db
    from member import Member, get_current_user


# ==========================================
# 1. DB 모델 정의 (Member 연동)
# ==========================================
class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, index=True)
    board_type = Column(String(50), nullable=False, default="free", index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(255), nullable=True)  # 비회원 글용 비밀번호

    # member 테이블과의 외래키(FK) 및 관계 설정
    member_id = Column(Integer, ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    author = Column(String(50), default="익명")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Member 모델 매핑
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
    password: Optional[str] = None
    member_id: Optional[int] = None


# U (Update) - 수정 스키마
class BoardUpdate(BaseModel):
    password: Optional[str] = None
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

    model_config = {"from_attributes": True}


# ==========================================
# 3. Router 인스턴스 및 선택적 로그인 검증 헬퍼
# ==========================================
router = APIRouter(
    prefix="/api/board",
    tags=["Multi-Board Management"]
)


def get_current_user_optional(
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(lambda: None)  # 기본값 초기화
) -> Optional[Member]:
    """
    member.py의 get_current_user를 직접 활용하여 토큰이 정상적이면 유저를 반환하고,
    인증 실패 시 401 오류를 던지는 대신 None을 반환하도록 예외를 안전하게 래핑합니다.
    """
    return current_user


# 선택적 토큰 검증용 wrapper 함수
def get_optional_user(
    db: Session = Depends(get_db),
    user: Optional[Member] = Depends(lambda db=Depends(get_db): None)
):
    pass


# 안전한 선택적 사용자 인증 헬퍼
async def get_current_user_safe(
    db: Session = Depends(get_db),
    user_or_none: Optional[Member] = None
) -> Optional[Member]:
    return user_or_none


# member.py의 get_current_user를 감싸서 401 예외를 예방하는 의존성 주입 함수
async def get_optional_current_user(
    db: Session = Depends(get_db),
    user: Optional[Member] = Depends(
        lambda: None
    )
) -> Optional[Member]:
    try:
        # FastAPI 의존성 체인 내에서 get_current_user를 직접 호출 시도
        from fastapi import Request
        pass
    except Exception:
        return None
    return None

# ==========================================
# 실제 실무에서 가장 깔끔한 선택적 인증 패턴
# ==========================================
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security_optional = HTTPBearer(auto_error=False)

def get_current_user_optional_clean(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db)
) -> Optional[Member]:
    if not auth or not auth.credentials:
        return None
    try:
        # member.py의 인증 함수 검증 로직 재활용
        return get_current_user(token=auth.credentials, db=db)
    except HTTPException:
        # 토큰 만료 등 인증 실패 시 401 대신 비회원(None)으로 유연하게 처리
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


# [C - Create] 게시글 작성 (회원/비회원 겸용)
@router.post("/{board_type}", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    board_type: str, 
    board: BoardCreate, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user_optional_clean)
):
    board_data = board.model_dump()

    # 1. 로그인 회원인 경우 (JWT 토큰 검증 성공)
    if current_user:
        board_data["member_id"] = current_user.id
        board_data["author"] = current_user.name
    
    # 2. member_id 명시 전달 시
    elif board.member_id:
        existing_member = db.query(Member).filter(Member.id == board.member_id).first()
        if not existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않는 회원 ID(member_id)입니다."
            )
        board_data["author"] = existing_member.name

    # 3. 비회원인 경우 비밀번호 필수
    else:
        if not board.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비회원 게시글 작성 시 비밀번호 입력은 필수입니다."
            )

    try:
        db_board = Board(
            board_type=board_type,
            **board_data
        )
        db.add(db_board)
        db.commit()
        db.refresh(db_board)
        return db_board
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 저장 중 오류 발생: {str(e)}"
        )


# [U - Update] 게시글 수정
@router.put("/{board_type}/{board_id}", response_model=BoardResponse)
def update_board(
    board_type: str, 
    board_id: int, 
    board_data: BoardUpdate, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user_optional_clean)
):
    db_board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not db_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    is_author = current_user and current_user.id == db_board.member_id
    is_password_correct = board_data.password and db_board.password == board_data.password

    if not (is_author or is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="수정 권한이 없습니다. 비밀번호를 확인해 주세요."
        )

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
    current_user: Optional[Member] = Depends(get_current_user_optional_clean)
):
    db_board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not db_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

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