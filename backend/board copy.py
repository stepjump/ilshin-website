from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel

try:
    from .main import Base, get_db
    from .member import Member, SECRET_KEY, ALGORITHM, verify_password, get_password_hash
except ImportError:
    from main import Base, get_db
    from member import Member, SECRET_KEY, ALGORITHM, verify_password, get_password_hash

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/members/login", auto_error=False)


class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, index=True)
    board_type = Column(String(50), nullable=False, default="free", index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(255), nullable=True)  # 비회원용 해시 비밀번호

    member_id = Column(Integer, ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    author = Column(String(50), default="손님")
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", backref="boards")


class BoardBase(BaseModel):
    title: str
    content: str


class BoardCreate(BoardBase):
    password: Optional[str] = None


class BoardUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    password: Optional[str] = None


class BoardDeleteRequest(BaseModel):
    password: Optional[str] = None


class BoardResponse(BoardBase):
    id: int
    board_type: str
    author: str
    member_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


router = APIRouter(
    prefix="/api/board",
    tags=["Multi-Board Management"]
)


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional), 
    db: Session = Depends(get_db)
) -> Optional[Member]:
    if not token:
        return None
    try:
        import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email:
            user = db.query(Member).filter(Member.email == email).first()
            if user and getattr(user, "is_active", "Y") == "Y":
                return user
    except Exception:
        return None
    return None


@router.get("/{board_type}", response_model=List[BoardResponse])
def get_boards_by_type(board_type: str, db: Session = Depends(get_db)):
    return db.query(Board).filter(Board.board_type == board_type).order_by(Board.id.desc()).all()


@router.get("/{board_type}/{board_id}", response_model=BoardResponse)
def get_board_by_id(board_type: str, board_id: int, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.board_type == board_type, Board.id == board_id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )
    return board


@router.post("/{board_type}", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    board_type: str, 
    board: BoardCreate, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user_optional)
):
    board_data = board.model_dump()

    if current_user:
        board_data["member_id"] = current_user.id
        board_data["author"] = getattr(current_user, "name", None) or getattr(current_user, "email", "회원")
        board_data["password"] = None
    else:
        if not board.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비회원 게시글 작성 시 비밀번호 입력은 필수입니다."
            )
        board_data["member_id"] = None
        board_data["author"] = "손님"
        # 비회원 글 비밀번호 해싱
        board_data["password"] = get_password_hash(board_data["password"])

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
    # 버그 수정: board_data.password와 db_board.password 해시값 검증
    is_password_correct = (
        board_data.password is not None 
        and db_board.password is not None 
        and verify_password(board_data.password, db_board.password)
    )

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
    # 버그 수정: delete_req.password 해시 검증
    is_password_correct = (
        delete_req.password is not None 
        and db_board.password is not None 
        and verify_password(delete_req.password, db_board.password)
    )

    if not (is_author or is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="삭제 권한이 없습니다. 비밀번호를 확인해 주세요."
        )

    db.delete(db_board)
    db.commit()
    return {"message": f"게시글(ID: {board_id})이 성공적으로 삭제되었습니다."}