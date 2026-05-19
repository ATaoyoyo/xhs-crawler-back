from ..models import db


class RevokedTokenModel(db.Model):
    """
    已过期token表
    """

    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), nullable=False)

    # token加黑
    def add(self):
        db.session.add(self)
        db.session.commit()

    # 加黑token查询
    @classmethod
    def is_jti_blacklisted(cls, jti):
        return bool(cls.query.filter_by(jti=jti).first())
