from ..models import db


class PostTagModel(db.Model):
    """
    笔记标签
    """

    __tablename__ = 'post_tag'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    tag_id = db.Column(db.String(255), unique=True, nullable=False, comment='标签ID')
    tag_name = db.Column(db.String(255), nullable=False, comment='标签名称')
    tag_type = db.Column(db.String(255), nullable=False, comment='标签类型')
    tag_count = db.Column(db.Integer(), nullable=False, comment='标签数量')

    @classmethod
    def add(cls, **kwargs):
        tag = cls(**kwargs)
        db.session.add(tag)
        db.session.commit()
        return tag

    @classmethod
    def find_by_tag_id(cls, tag_id):
        return cls.query.filter_by(tag_id=tag_id).first()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def dict(self):
        return {
            "id": self.id,
            "tagId": self.tag_id,
            "tagName": self.tag_name,
            "tagType": self.tag_type,
            "tagCount": self.tag_count,
        }
