from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel

# main.py 및 member.py에서 정의된 Base, get_db, Member 불러오기
from main import Base, get_db
from member import Member


# ==========================================
# 1. DB 모델 정의 (Member 연동 및 password 추가)
# ==========================================
class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, index=True)
    board_type = Column(String(50), nullable=False, default="free", index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(255), nullable=False)  # 게시글 수정/삭제용 비밀번호
    
    # member 테이블과의 외래키(FK) 설정
    member_id = Column(Integer, ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    author = Column(String(50), default="익명")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Member 모델과의 관계(Relationship) 매핑
    member = relationship("Member", backref="boards")


# ==========================================
# 2. Pydantic 스키마 정의
# ==========================================
class BoardBase(BaseModel):
    title: str
    content: str
    author: Optional[str] = "익명"


# C (Create) - 작성 시 비밀번호 및 회원 ID 입력
class BoardCreate(BoardBase):
    password: str
    member_id: Optional[int] = None  # 회원인 경우 member_id 전달 가능


# U (Update) - 수정 시 비밀번호 검증 필수
class BoardUpdate(BaseModel):
    password: str  # 본인 확인용 비밀번호
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None


# D (Delete) - 삭제 요청 데이터 (비밀번호 전송용)
class BoardDeleteRequest(BaseModel):
    password: str


# R (Response) - 게시글 응답용 (보안을 위해 password는 제외!)
class BoardResponse(BoardBase):
    id: int
    board_type: str
    member_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# 3. Router 인스턴스 생성
# ==========================================
router = APIRouter(
    prefix="/api/board",
    tags=["Multi-Board Management"]
)


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
            detail="Board post not found"
        )
    return board


# [C - Create] 게시글 작성 (비밀번호 설정 포함)
@router.post("/{board_type}", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(board_type: str, board: BoardCreate, db: Session = Depends(get_db)):
    # member_id가 넘어온 경우 해당 회원이 존재하는지 검증
    if board.member_id:
        existing_member = db.query(Member).filter(Member.id == board.member_id).first()
        if not existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid member_id. Member does not exist."
            )
        # 회원 이름이 있다면 작성자명(author) 자동 동기화 (원하는 경우)
        if not board.author or board.author == "익명":
            board.author = existing_member.name

    db_board = Board(
        board_type=board_type,
        **board.model_dump()
    )
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


# [U - Update] 게시글 수정 (비밀번호 검증 필수)
@router.put("/{board_type}/{board_id}", response_model=BoardResponse)
def update_board(board_type: str, board_id: int, board_data: BoardUpdate, db: Session = Depends(get_db)):
    db_board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not db_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board post not found"
        )

    # 비밀번호 일치 여부 확인
    if db_board.password != board_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password for this post"
        )

    # 비밀번호 검증 성공 후 변경 데이터만 업데이트 (password 필드 제외)
    update_data = board_data.model_dump(exclude_unset=True, exclude={"password"})
    for key, value in update_data.items():
        setattr(db_board, key, value)

    db.commit()
    db.refresh(db_board)
    return db_board


# [D - Delete] 게시글 삭제 (HTTP POST/DELETE Body로 비밀번호 전송)
@router.post("/{board_type}/{board_id}/delete", status_code=status.HTTP_200_OK)
def delete_board(board_type: str, board_id: int, delete_req: BoardDeleteRequest, db: Session = Depends(get_db)):
    db_board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not db_board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board post not found"
        )

    # 비밀번호 일치 여부 확인
    if db_board.password != delete_req.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password for this post"
        )

    db.delete(db_board)
    db.commit()
    return {"message": f"Board ID {board_id} has been deleted successfully"}

