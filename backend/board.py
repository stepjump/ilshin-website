import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel

try:
    from .main import Base, get_db
    from .member import get_current_user, Member
except ImportError:
    from main import Base, get_db
    from member import get_current_user, Member

# 1. DB 모델 정의
class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_email = Column(String(150), nullable=False)
    author_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 2. Pydantic 스키마 정의
class BoardBase(BaseModel):
    title: str
    content: str


class BoardCreate(BoardBase):
    pass


class BoardResponse(BoardBase):
    id: int
    author_email: str
    author_name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 3. Router 인스턴스
router = APIRouter(
    prefix="/api/board",
    tags=["Board Management"]
)


# 4. API 엔드포인트
@router.get("", response_model=List[BoardResponse])
def get_all_posts(db: Session = Depends(get_db)):
    """전체 게시글 목록 조회"""
    return db.query(Board).order_by(Board.created_at.desc()).all()


@router.get("/{post_id}", response_model=BoardResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """단일 게시글 상세 조회"""
    post = db.query(Board).filter(Board.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="게시글을 찾을 수 없습니다."
        )
    return post


@router.post("", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: BoardCreate, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user)
):
    """게시글 작성 (로그인 필수)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )

    db_post = Board(
        title=post.title,
        content=post.content,
        author_email=current_user.email,
        author_name=current_user.name
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


# ★ 5. 단일 게시글 삭제 (자신의 게시글만 OR admin 등급인 경우 삭제 가능)
@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )

    post = db.query(Board).filter(Board.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="게시글을 찾을 수 없습니다."
        )

    # 작성자 본인 여부 및 admin 여부 판단
    is_owner = (post.author_email == current_user.email)
    is_admin = (current_user.role == "admin")

    # 자신의 글이 아니면서 admin도 아닌 경우는 삭제 권한 거부
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 게시글만 삭제할 수 있습니다. (admin 계정은 제외)"
        )

    db.delete(post)
    db.commit()
    return {"message": "게시글이 성공적으로 삭제되었습니다."}


# ★ 6. 게시판 전체 삭제 (admin 등급 전용)
@router.delete("/all", status_code=status.HTTP_200_OK)
def delete_all_posts(
    db: Session = Depends(get_db),
    current_user: Optional[Member] = Depends(get_current_user)
):
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자(admin) 등급만 전체 삭제 권한이 있습니다."
        )

    deleted_count = db.query(Board).delete()
    db.commit()

    return {
        "message": f"총 {deleted_count}개의 모든 게시글이 삭제되었습니다.",
        "deleted_count": deleted_count
    }