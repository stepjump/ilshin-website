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
    from .member import Member, SECRET_KEY, ALGORITHM
except ImportError:
    from main import Base, get_db
    from member import Member, SECRET_KEY, ALGORITHM

# 비회원 작성 허용을 위한 auto_error=False OAuth2 스킴
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/members/login", auto_error=False)


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
    author = Column(String(50), default="손님")  # 기본 작성자 명칭: 손님
    created_at = Column(DateTime, default=datetime.utcnow)

    # Member 모델 매핑
    member = relationship("Member", backref="boards")


# ==========================================
# 2. Pydantic 스키마 정의
# ==========================================
class BoardBase(BaseModel):
    title: str
    content: str


# C (Create) - 작성 스키마 (member_id, author는 서버에서 자동 바인딩)
class BoardCreate(BoardBase):
    password: Optional[str] = None  # 비회원 작성 시 필수


# U (Update) - 수정 스키마
class BoardUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    password: Optional[str] = None  # 비회원 글 수정시 비밀번호 검증용


# D (Delete) - 삭제 요청 스키마
class BoardDeleteRequest(BaseModel):
    password: Optional[str] = None


# R (Response) - 응답 스키마
class BoardResponse(BoardBase):
    id: int
    board_type: str
    author: str
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
    token: Optional[str] = Depends(oauth2_scheme_optional), 
    db: Session = Depends(get_db)
) -> Optional[Member]:
    """
    토큰이 유효하면 유저 정보를 반환하고,
    토큰이 없거나 유효하지 않으면 401 에러 대신 None을 반환하여 비회원 처리합니다.
    """
    if not token:
        return None
    try:
        import jwt  # PyJWT 사용시
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email:
            user = db.query(Member).filter(Member.email == email).first()
            if user and getattr(user, "is_active", "Y") == "Y":
                return user
    except Exception:
        try:
            from jose import jwt as jose_jwt
            payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email:
                user = db.query(Member).filter(Member.email == email).first()
                if user and getattr(user, "is_active", "Y") == "Y":
                    return user
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


# [C - Create] 게시글 작성 (회원/비회원 겸용)
@router.post("/{board_type}", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    board_type: str, 
    board: BoardCreate, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user_optional)
):
    board_data = board.model_dump()

    # 1. 로그인 회원인 경우 -> member_id 및 회원 이름 자동 설정
    if current_user:
        board_data["member_id"] = current_user.id
        board_data["author"] = getattr(current_user, "name", None) or getattr(current_user, "email", "회원")
        board_data["password"] = None  # 회원 글은 비밀번호 불필요

    # 2. 비회원인 경우 -> member_id는 None, author는 "손님"으로 자동 지정
    else:
        if not board.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비회원 게시글 작성 시 비밀번호 입력은 필수입니다."
            )
        board_data["member_id"] = None
        board_data["author"] = "손님"

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
    current_user: Optional[Member] = Depends(get_current_user_optional)
):
    db_board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not db_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    is_author = current_user and current_user.id == db_board.member_id
    is_password_correct = board_data.password and db_board.password == db_board.password

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
    current_user: Optional[Member] = Depends(get_current_user_optional)
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