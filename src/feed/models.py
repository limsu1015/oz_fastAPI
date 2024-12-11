from datetime import datetime

from sqlalchemy import Integer, Column, Text, String, DateTime, ForeignKey
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