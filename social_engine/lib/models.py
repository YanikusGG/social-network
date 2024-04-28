from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    text = Column(String)
    user_id = Column(Integer, nullable=False)
    creation_time = Column(TIMESTAMP, nullable=False)

    comments = relationship("Comments")

    def fill_proto(self, proto_post):
        proto_post.id = self.id
        proto_post.title = self.title
        proto_post.text = self.text
        proto_post.user_id = self.user_id
        proto_post.creation_time.FromDatetime(self.creation_time)

class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    user_id = Column(Integer, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    reply_id = Column(Integer, ForeignKey("comments.id"))
    creation_time = Column(TIMESTAMP, nullable=False)

    post = relationship("Posts")
    reply_comment = relationship("Comments")
