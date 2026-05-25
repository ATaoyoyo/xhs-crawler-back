from ..models import db
from datetime import datetime


class SpiderLogModel(db.Model):
    """
    爬虫请求日志表
    """
    __tablename__ = 'spider_log'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    post_id = db.Column(db.String(255), comment='关联的笔记ID')
    client_type = db.Column(db.String(50), nullable=False, default='unknown', comment='客户端类型: miniprogram/web/unknown')
    request_ip = db.Column(db.String(255), comment='请求IP')
    request_url = db.Column(db.Text(), comment='请求的笔记URL')
    status = db.Column(db.String(50), nullable=False, default='success', comment='请求状态: success/failed')
    error_message = db.Column(db.Text(), comment='错误信息')
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.now, comment='创建时间')

    @classmethod
    def add(cls, **kwargs):
        log = cls(**kwargs)
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def get_by_post_id(cls, post_id):
        return cls.query.filter_by(post_id=post_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_stats_by_client_type(cls):
        """按客户端类型统计调用次数"""
        from sqlalchemy import func
        return db.session.query(
            cls.client_type,
            func.count(cls.id).label('count')
        ).group_by(cls.client_type).all()

    def dict(self):
        return {
            "id": self.id,
            "postId": self.post_id,
            "clientType": self.client_type,
            "requestIp": self.request_ip,
            "requestUrl": self.request_url,
            "status": self.status,
            "errorMessage": self.error_message,
            "createdAt": int(self.created_at.timestamp() * 1000) if self.created_at else None,
        }