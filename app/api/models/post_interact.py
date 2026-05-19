from ..models import db


class PostInteractModel(db.Model):
    """
    笔记互动信息统计
    """

    __tablename__ = 'post_interact'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    post_id = db.Column(db.String(255), db.ForeignKey('post_detail.post_id'), nullable=False, comment='笔记ID')
    collected_count = db.Column(db.String(255), nullable=False, comment='笔记收藏数')
    comment_count = db.Column(db.String(255), nullable=False, comment='笔记评论数')
    share_count = db.Column(db.String(255), nullable=False, comment='笔记分享数')
    liked_count = db.Column(db.String(255), nullable=False, comment='笔记点赞数')

    @classmethod
    def add(cls, **kwargs):
        interact = cls(**kwargs)
        db.session.add(interact)
        db.session.commit()
        return interact

    @classmethod
    def find_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def find_by_post_id(cls, post_id):
        return cls.query.filter_by(post_id=post_id).first()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def dict(self):
        return {
            "id": self.id,
            "postId": self.post_id,
            "collectedCount": self.collected_count,
            "commentCount": self.comment_count,
            "shareCount": self.share_count,
            "likedCount": self.liked_count
        }
