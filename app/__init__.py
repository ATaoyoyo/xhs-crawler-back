import os

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

from .config import config
from .api import api_blueprint
from .api.models import db
from migrations import migrate
from .utils.logger import log

from .spider.scheduler import init_scheduler

# 数据库模型
from .api.models.post_detail import PostDetailModel
from .api.models.post_media import PostMediaModel
from .api.models.post_interact import PostInteractModel
from .api.models.post_tag import PostTagModel
from .api.models.post_user import PostUserModel

from .api.models.user import UserModel
from .api.models.revoked_token import RevokedTokenModel

load_dotenv()


def create_app(config_name):
    app = Flask(__name__)

    # 跨域
    CORS(app)

    # 环境配置
    log.info(f'当前项目环境: {config_name}')
    app.config.from_object(config[config_name])

    # 初始化
    db.init_app(app)
    migrate.init_app(app, db)

    # 蓝图注册
    app.register_blueprint(api_blueprint)

    # 爬虫调度
    init_scheduler(app)

    # 初始化 JWT
    jwt = JWTManager(app)
    # 注册 JWT 钩子
    register_jwt_hooks(jwt)

    return app


# 注册 JWT 钩子 用于检查 token 是否在黑名单中
def register_jwt_hooks(jwt):
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, decrypted_token):
        jti = decrypted_token['jti']
        return RevokedTokenModel.is_jti_blacklisted(jti)


app = create_app(os.getenv('FLASK_ENV'))
