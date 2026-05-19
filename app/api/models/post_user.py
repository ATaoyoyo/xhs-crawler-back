from ..models import db


class PostUserModel(db.Model):
    """
    笔记用户
    """
    __tablename__ = 'post_user'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.String(255), unique=True, nullable=False, comment='用户ID')
    user_name = db.Column(db.String(255), nullable=False, comment='用户名')
    user_avatar = db.Column(db.String(255), nullable=False, comment='用户头像')
    user_xsec_token = db.Column(db.String(255), nullable=False, comment='用户XSEC_TOKEN')

    def dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'userName': self.user_name,
            'userAvatar': self.user_avatar,
            'userXsecToken': self.user_xsec_token
        }

    @classmethod
    def add(cls, **kwargs):
        user = cls(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()
