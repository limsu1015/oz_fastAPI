from datetime import datetime

from sqlalchemy import Integer, Column, Text, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from config.database.orm import Base
from user.models import User


class Post(Base):
    __tablename__ = 'feed_posts'

    # 실제 db 컬럼
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('service_user.id'), nullable=False)
    image = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # orm 관계 정의
    user = relationship(User, backref="posts")

    @property # 커스텀하게 정의하는 속성
    def image_static_path(self) -> str:
        filename: str = self.image.split("/")[-1]
        return f"http://127.0.0.1:8000/static/{filename}"



# 관계키 ForeignKey

    @classmethod
    def create(cls, user_id: int, image: str, content: str):
        return cls(user_id=user_id, image=image, content=content)


    def update_content(self, content: str):

        if "f-word" in content:
            raise ValueError("Content should not contain f-word")

        self.content = content


class PostComment(Base):
    __tablename__ = 'posts_comments'

    id = Column(Integer, primary_key=True)
    # 댓글 작성자
    user_id = Column(Integer, ForeignKey('service_user.id'), nullable=False)
    # 게시글
    post_id = Column(Integer, ForeignKey('feed_posts.id'), nullable=False)
    content = Column(Text, nullable=False) # 댓글 내용

    # 댓글 - 대댓글
    parent_id = Column(Integer, ForeignKey('posts_comments.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    post = relationship(Post, backref="comments")
    parent = relationship("PostComment", remote_side=[id], backref="replies")

    @property
    def is_parent(self) -> bool:
        return self.parent_id is None


    @classmethod
    def create(
            cls, user_id: int, post_id: int, content: str, parent_id: int | None
    ):
        return cls(
            user_id=user_id,
            post_id=post_id,
            content=content,
            parent_id=parent_id
        )

class PostLike(Base):
    __tablename__ = 'posts_likes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('service_user.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('feed_posts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    __table_args__ = (
        # 사용자는 하나의 게시글에는 한번만 좋아요를 생성할 수 있음
        UniqueConstraint("user_id", "post_id", name="uq_post_like_user_post"),
    )

    @classmethod
    def create(cls, user_id: int, post_id: int):
        return cls(user_id=user_id, post_id=post_id)

# 사용자가 like 버튼 -> PostLike(user_id, post_id)기록
# 중복 생성 방지
# 사용자가 Like 버튼 취소 -> PostLike(user_id, post_id) 삭제