from ..models import db
from sqlalchemy import func
from datetime import datetime


class UserModel(db.Model):
    """
    用户表
    """

    __tablename__ = "user"

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment="主键ID")
    user_name = db.Column(db.String(255), nullable=False, unique=True, comment="用户名称")
    user_pwd = db.Column(db.String(255), nullable=False, comment="用户密码")
    salt = db.Column(db.String(255), comment="salt")
    # 创建时间
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.now, comment='创建时间')
      # 更新时间
    updated_at = db.Column(db.DateTime(), nullable=False, default=datetime.now, onupdate=datetime.now,
                              comment='更新时间')


    def add_user(self):
        db.session.add(self)
        db.session.commit()

    def dict(self):
        return {
            "id": self.id,
            "userName": self.user_name,
            "createAt": datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            "updateAt": datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }

    def getPwd(self):
        return {"pwd": self.user_pwd, "salt": self.salt}


    @classmethod
    def find_by_user_name(cls, user_name):
        return cls.query.filter_by(user_name=user_name).first()

    @classmethod
    def find_all_user(cls):
        return cls.query.all()




