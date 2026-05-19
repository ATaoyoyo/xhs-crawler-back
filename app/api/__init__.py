from flask import Blueprint
from flask_restful import Api
from .resources.spider import SpiderListAPI, SpiderDetailAPI
from .resources.user import UserRegisterAPI, UserLoginAPI, UserLogoutAPI, UserListApi
from .resources.admin import (
    AdminLoginResource,
    AdminLogoutResource,
    AdminRefreshResource,
    DashboardStatsResource,
    PostListResource,
    PostDetailResource,
    UserListResource,
)

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_blueprint)

# 爬虫接口
api.add_resource(SpiderListAPI, '/spider')
api.add_resource(SpiderDetailAPI, '/spider/<string:post_id>')

# 后台用户接口
api.add_resource(UserRegisterAPI, '/user')
api.add_resource(UserLoginAPI, '/user/login', '/refreshToken')
api.add_resource(UserLogoutAPI, '/user/logout')
api.add_resource(UserListApi, '/user/list')

# 管理端接口
api.add_resource(AdminLoginResource, '/admin/login')
api.add_resource(AdminLogoutResource, '/admin/logout')
api.add_resource(AdminRefreshResource, '/admin/refresh')
api.add_resource(DashboardStatsResource, '/admin/dashboard/stats')
api.add_resource(PostListResource, '/admin/posts')
api.add_resource(PostDetailResource, '/admin/posts/<string:post_id>')
api.add_resource(UserListResource, '/admin/users')
