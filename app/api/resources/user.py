import uuid
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash

from ..models.user import UserModel
from ..models.revoked_token import RevokedTokenModel

from ..response import send_success, send_error, send_server_error
from ..schema.register_sha import register_sha, reg_args_valid


class UserRegisterAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        register_sha(parser)
        args = parser.parse_args()

        if UserModel.find_by_user_name(args['username']):
            return send_error('用户已存在!')
        else:
            try:
                args['salt'] = uuid.uuid4().hex
                args['password'] = generate_password_hash('{}{}'.format(args['salt'], args['password']))
                user_data = {"user_name": args['username'], "user_pwd": args['password'], "salt": args['salt']}
                user = UserModel(**user_data)
                user.add_user()
                return send_success('用户创建成功!')
            except Exception as e:
                return send_server_error(str(e))

    @jwt_required(refresh=True)
    def get(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return send_success({"access_token": f"Bearer {access_token}"})


class UserLoginAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        reg_args_valid(parser)
        args = parser.parse_args()

        try:
            exit_user = UserModel.find_by_user_name(args['username'])
            if exit_user:
                salt = exit_user.getPwd().get('salt')
                pwd = exit_user.getPwd().get('pwd')
                valid = check_password_hash(pwd, '{}{}'.format(salt, args['password']))
                print(valid)
                if valid:
                    token = generateToken(args['username'])
                    return send_success(token)
                else:
                    return send_error('用户名密码错误!')
            else:
                return send_error('用户不存在!')
        except Exception as e:
            send_server_error(str(e))


class UserLogoutAPI(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return send_success()
        except Exception as e:
            return send_error(str(e))


def generateToken(id):
    access_token = create_access_token(identity=id)
    refresh_token = create_refresh_token(identity=id)
    return {
        'accessToken': 'Bearer ' + access_token,
        'refreshToken': 'Bearer ' + refresh_token,
    }


class UserListApi(Resource):
    @jwt_required()
    def get(self):
        users = []
        try:
            user_list = UserModel.find_all_user()
            for user in user_list:
                users.append(user.dict())
            return send_success(users)
        except Exception as e:
            return send_server_error(str(e))
