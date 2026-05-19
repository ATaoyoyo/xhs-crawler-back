from ..models import db


class PostMediaModel(db.Model):
    """
    笔记媒体表
    """
    __tablename__ = 'post_media'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    post_id = db.Column(db.String(255), db.ForeignKey('post_detail.post_id'), nullable=False, comment='笔记ID')
    post_images = db.Column(db.Text(), nullable=True, comment='笔记图片')
    post_videos = db.Column(db.Text(), nullable=True, comment='笔记视频')

    @classmethod
    def add(cls, **kwargs):
        media = cls(**kwargs)
        db.session.add(media)
        db.session.commit()
        return media

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
            "postImages": self.post_images.split(',') if self.post_images else [],
            "postVideos": self.post_videos.split(',') if self.post_videos else [],
        }
