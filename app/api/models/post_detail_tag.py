from ..models import db


class PostDetailTagModel(db.Model):
    """
    笔记与标签的关联表
    """
    __tablename__ = 'post_detail_tag'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    post_id = db.Column(db.String(255), db.ForeignKey('post_detail.post_id'), nullable=False, comment='笔记ID')
    tag_id = db.Column(db.String(255), db.ForeignKey('post_tag.tag_id'), nullable=False, comment='标签ID')

    __table_args__ = (
        db.Index('idx_post_id', 'post_id'),
        db.Index('idx_tag_id', 'tag_id'),
        db.UniqueConstraint('post_id', 'tag_id', name='uq_post_tag'),
    )

    @classmethod
    def add(cls, post_id, tag_id):
        item = cls(post_id=post_id, tag_id=tag_id)
        db.session.add(item)
        return item

    @classmethod
    def delete_by_post_id(cls, post_id):
        cls.query.filter_by(post_id=post_id).delete()

    @classmethod
    def get_tags_by_post_id(cls, post_id):
        return cls.query.filter_by(post_id=post_id).all()
