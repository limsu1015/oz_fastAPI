from fastapi import Depends
from sqlalchemy.orm import Session

from config.database.connection import get_session
from feed.models import Post, PostComment


class PostRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def save(self, post: Post) -> None:
        self.session.add(post)
        self.session.commit()

    def get_posts(self):
        return self.session.query(Post).order_by(Post.created_at.desc()).all()


    def get_post(self, post_id: int) -> Post | None:
        return self.session.query(Post).filter_by(id=post_id).first()





    def delete(self, post: Post) -> None:
        self.session.delete(post)
        self.session.commit()

    def delete_my_post(self, post_id: int, user_id: int) -> None:
        self.session.query(Post).filter_by(id=post_id, user_id=user_id).delete()
        self.session.commit()

class PostCommentRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def save(self, comment: PostComment) -> None:
        self.session.add(comment)
        self.session.commit()

    def get_comment(self, comment_id: int) -> PostComment | None:
        return self.session.query(PostComment).filter_by(id=comment_id).first()