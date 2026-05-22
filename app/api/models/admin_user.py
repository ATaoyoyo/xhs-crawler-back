from ..models import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class AdminUserModel(db.Model):
    """
    管理员用户表
    """

    __tablename__ = "admin_user"

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment="主键ID")
    username = db.Column(db.String(255), nullable=False, unique=True, comment="管理员用户名")
    password = db.Column(db.String(255), nullable=False, comment="管理员密码")
    salt = db.Column(db.String(255), comment="盐值")
    role = db.Column(db.String(50), default="admin", comment="角色")
    is_active = db.Column(db.Boolean, default=True, comment="是否激活")
    last_login_at = db.Column(db.DateTime, comment="最后登录时间")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "isActive": self.is_active,
            "lastLoginAt": datetime.strftime(self.last_login_at, "%Y-%m-%d %H:%M:%S") if self.last_login_at else None,
            "createdAt": datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            "updatedAt": datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }

    def verify_password(self, input_password):
        # input_password 是前端传来的 SHA256(明文密码)
        # 数据库存储格式: hash(salt + SHA256(明文密码))
        return check_password_hash(self.password, '{}{}'.format(self.salt, input_password))

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.get(id)