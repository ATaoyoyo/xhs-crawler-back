from ..models import db
from datetime import datetime
from sqlalchemy import func


class PostDetailModel(db.Model):
    """
    爬虫笔记表
    """
    __tablename__ = 'post_detail'

    # 主键ID
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    # 笔记信息
    post_id = db.Column(db.String(255), unique=True, nullable=False, comment='笔记ID')
    post_title = db.Column(db.String(255), comment='笔记标题')
    post_content = db.Column(db.Text(), comment='笔记内容')
    post_share_url = db.Column(db.String(255), nullable=False, comment='笔记链接')
    post_date = db.Column(db.DateTime(), nullable=False, comment='笔记发布时间')
    post_updated = db.Column(db.DateTime(), comment='笔记更新时间')
    post_author_id = db.Column(db.String(255), nullable=False, comment='笔记作者ID')
    post_at_user_id = db.Column(db.String(255), comment='笔记被@用户ID')
    post_category = db.Column(db.String(255), comment='笔记分类')
    post_tags_id = db.Column(db.Text(), comment='笔记标签')
    post_ip = db.Column(db.String(255), comment='笔记IP')
    # 创建时间
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.now, comment='创建时间')
    # 更新时间
    updated_at = db.Column(db.DateTime(), nullable=False, default=datetime.now, onupdate=datetime.now,
                           comment='更新时间')

    # post_comment_status = db.Column(db.String(255), nullable=False, comment='笔记评论状态')
    # post_comment_count = db.Column(db.Integer, nullable=False, comment='笔记评论数')
    # post_thumbnail = db.Column(db.String(255), nullable=False, comment='笔记缩略图')

    @classmethod
    def add(cls, **kwargs):
        post = cls(**kwargs)
        db.session.add(post)
        db.session.commit()
        return post

    @classmethod
    def get_post_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_post_by_title(cls, post_title):
        return cls.query.filter_by(post_title=post_title).first()

    @classmethod
    def get_post_by_post_id(cls, post_id):
        return cls.query.filter_by(post_id=post_id).first()

    @classmethod
    def get_all_posts(cls):
        return cls.query.all()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(post):
        db.session.delete(post)
        db.session.commit()

    def dict(self):
        return {
            "id": self.id,
            "postId": self.post_id,
            "title": self.post_title,
            "content": self.post_content,
            "shareUrl": self.post_share_url,
            "date": int(self.post_date.timestamp() * 1000),
            "updated": int(self.post_updated.timestamp() * 1000),
            "authorId": self.post_author_id,
            "atUsersId": self.post_at_user_id.split(',') if self.post_at_user_id else [],
            "category": self.post_category,
            "tagsId": self.post_tags_id.split(',') if self.post_tags_id else [],
            "ip": self.post_ip,
        }
