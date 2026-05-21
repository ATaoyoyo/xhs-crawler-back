import uuid
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from ..models.admin_user import AdminUserModel
from ..models.revoked_token import RevokedTokenModel
from ..models.post_detail import PostDetailModel
from ..models.post_interact import PostInteractModel
from ..models.post_tag import PostTagModel
from ..models.post_user import PostUserModel
from ..models.user import UserModel
from ..models import db
from ..models.post_detail_tag import PostDetailTagModel

from ..response import send_success, send_error, send_server_error


def generate_admin_token(username):
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return {
        'accessToken': 'Bearer ' + access_token,
        'refreshToken': 'Bearer ' + refresh_token,
    }


class AdminLoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, location='json')
        parser.add_argument('password', type=str, required=True, location='json')
        args = parser.parse_args()

        try:
            admin = AdminUserModel.find_by_username(args['username'])
            if admin:
                if not admin.is_active:
                    return send_error('账户已被禁用')

                if admin.verify_password(args['password']):
                    admin.update(last_login_at=datetime.now())
                    token = generate_admin_token(admin.username)
                    return send_success(token)
                else:
                    return send_error('用户名或密码错误')
            else:
                return send_error('管理员不存在')
        except Exception as e:
            return send_server_error(str(e))


class AdminLogoutResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return send_success('登出成功')
        except Exception as e:
            return send_error(str(e))


class AdminRefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return send_success({'accessToken': 'Bearer ' + access_token})


class AdminCurrentUserResource(Resource):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        admin = AdminUserModel.find_by_username(username)
        if not admin:
            return send_error('用户不存在')
        return send_success({
            'id': admin.id,
            'username': admin.username,
            'role': admin.role
        })


class DashboardStatsResource(Resource):
    @jwt_required()
    def get(self):
        try:
            total_posts = PostDetailModel.query.count()
            total_users = UserModel.query.count()

            today = datetime.now().date()
            week_ago = today.replace(day=today.day - 6) if today.day >= 7 else today
            month_ago = today.replace(month=today.month - 1) if today.month >= 2 else today.replace(day=28)

            today_start = datetime.combine(today, datetime.min.time())
            week_start = datetime.combine(week_ago, datetime.min.time())
            month_start = datetime.combine(month_ago, datetime.min.time())

            today_downloads = db.session.query(
                db.func.count(db.distinct(PostInteractModel.post_id))
            ).join(
                PostDetailModel, PostDetailModel.post_id == PostInteractModel.post_id
            ).filter(
                PostDetailModel.created_at >= today_start
            ).scalar()

            week_downloads = db.session.query(
                db.func.count(db.distinct(PostInteractModel.post_id))
            ).join(
                PostDetailModel, PostDetailModel.post_id == PostInteractModel.post_id
            ).filter(
                PostDetailModel.created_at >= week_start
            ).scalar()

            month_downloads = db.session.query(
                db.func.count(db.distinct(PostInteractModel.post_id))
            ).join(
                PostDetailModel, PostDetailModel.post_id == PostInteractModel.post_id
            ).filter(
                PostDetailModel.created_at >= month_start
            ).scalar()

            posts_7days = db.session.query(
                db.func.date(PostDetailModel.created_at).label('date'),
                db.func.count().label('count')
            ).filter(
                PostDetailModel.created_at >= week_start
            ).group_by(
                db.func.date(PostDetailModel.created_at)
            ).all()

            trend_data = [{'date': str(p.date), 'count': p.count} for p in posts_7days]

            tag_counts = db.session.query(
                PostTagModel.tag_name,
                db.func.count().label('count')
            ).join(
                PostDetailTagModel,
                PostDetailTagModel.tag_id == PostTagModel.tag_id
            ).group_by(
                PostTagModel.tag_name
            ).order_by(
                db.desc('count')
            ).limit(10).all()

            top_tags = [{'name': t.tag_name, 'count': t.count} for t in tag_counts]

            return send_success({
                'totalPosts': total_posts,
                'totalUsers': total_users,
                'todayDownloads': today_downloads,
                'weekDownloads': week_downloads,
                'monthDownloads': month_downloads,
                'trendData': trend_data,
                'topTags': top_tags,
            })
        except Exception as e:
            return send_server_error(str(e))


class PostListResource(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('pageSize', type=int, default=20, location='args')
        parser.add_argument('keyword', type=str, default='', location='args')
        parser.add_argument('category', type=str, default='', location='args')
        parser.add_argument('author', type=str, default='', location='args')
        parser.add_argument('tag', type=str, default='', location='args')
        parser.add_argument('startDate', type=str, default='', location='args')
        parser.add_argument('endDate', type=str, default='', location='args')
        args = parser.parse_args()

        try:
            query = PostDetailModel.query

            if args['keyword']:
                keyword = f'%{args["keyword"]}%'
                query = query.filter(
                    db.or_(
                        PostDetailModel.post_title.like(keyword),
                        PostDetailModel.post_id.like(keyword)
                    )
                )

            if args['category']:
                query = query.filter(PostDetailModel.post_category == args['category'])

            if args['author']:
                author_keyword = f'%{args["author"]}%'
                matched_users = PostUserModel.query.filter(
                    db.or_(
                        PostUserModel.user_name.like(author_keyword),
                        PostUserModel.user_id.like(author_keyword)
                    )
                ).all()
                author_ids = [u.user_id for u in matched_users]
                if author_ids:
                    query = query.filter(PostDetailModel.post_author_id.in_(author_ids))
                else:
                    query = query.filter(db.false())

            if args['tag']:
                tag_keyword = f'%{args["tag"]}%'
                matched_tags = PostTagModel.query.filter(
                    PostTagModel.tag_name.like(tag_keyword)
                ).all()
                tag_ids = [t.tag_id for t in matched_tags]
                if tag_ids:
                    matched_post_ids = db.session.query(PostDetailTagModel.post_id).filter(
                        PostDetailTagModel.tag_id.in_(tag_ids)
                    ).distinct().all()
                    post_ids_filter = [p.post_id for p in matched_post_ids]
                    query = query.filter(PostDetailModel.post_id.in_(post_ids_filter))
                else:
                    query = query.filter(db.false())

            if args['startDate']:
                start = datetime.strptime(args['startDate'], '%Y-%m-%d')
                query = query.filter(PostDetailModel.created_at >= start)

            if args['endDate']:
                end = datetime.strptime(args['endDate'], '%Y-%m-%d')
                query = query.filter(PostDetailModel.created_at <= end)

            total = query.count()
            posts = query.order_by(PostDetailModel.created_at.desc()).offset(
                (args['page'] - 1) * args['pageSize']
            ).limit(args['pageSize']).all()

            # 批量查询，避免 N+1 问题
            post_ids = [post.post_id for post in posts]
            author_ids = [post.post_author_id for post in posts]
            all_tag_ids = []
            for post in posts:
                if post.post_tags_id:
                    all_tag_ids.extend([tid.strip() for tid in post.post_tags_id.split(',')])

            # 批量获取 interact 数据
            interact_map = {}
            if post_ids:
                interacts = PostInteractModel.query.filter(PostInteractModel.post_id.in_(post_ids)).all()
                interact_map = {i.post_id: i for i in interacts}

            # 批量获取 user 数据
            user_map = {}
            if author_ids:
                users = PostUserModel.query.filter(PostUserModel.user_id.in_(author_ids)).all()
                user_map = {u.user_id: u for u in users}

            # 批量获取 tag 数据
            tag_map = {}
            if all_tag_ids:
                tags = PostTagModel.query.filter(PostTagModel.tag_id.in_(all_tag_ids)).all()
                tag_map = {t.tag_id: t for t in tags}

            items = []
            for post in posts:
                interact = interact_map.get(post.post_id)
                post_user = user_map.get(post.post_author_id)
                tag_ids = post.post_tags_id.split(',') if post.post_tags_id else []
                tags = [tag_map[tid.strip()].dict() for tid in tag_ids if tid.strip() in tag_map]
                items.append({
                    'id': post.id,
                    'postId': post.post_id,
                    'title': post.post_title,
                    'authorName': post_user.user_name if post_user else post.post_author_id,
                    'authorAvatar': post_user.user_avatar if post_user else None,
                    'ip': post.post_ip,
                    'likedCount': interact.liked_count if interact else '0',
                    'collectedCount': interact.collected_count if interact else '0',
                    'tags': tags,
                    'downloadTime': datetime.strftime(post.created_at, '%Y-%m-%d %H:%M:%S'),
                })

            return send_success({
                'items': items,
                'total': total,
                'page': args['page'],
                'pageSize': args['pageSize'],
            })
        except Exception as e:
            return send_server_error(str(e))


class PostDetailResource(Resource):
    @jwt_required()
    def get(self, post_id):
        try:
            post = PostDetailModel.get_post_by_post_id(post_id)
            if not post:
                return send_error('笔记不存在')

            interact = PostInteractModel.find_by_post_id(post_id)
            from ..models.post_media import PostMediaModel
            media = PostMediaModel.find_by_post_id(post_id)
            post_user = PostUserModel.find_by_user_id(post.post_author_id)
            tag_ids = post.post_tags_id.split(',') if post.post_tags_id else []
            tags = []
            for tag_id in tag_ids:
                tag = PostTagModel.find_by_tag_id(tag_id.strip())
                if tag:
                    tags.append(tag.dict())

            data = {
                'id': post.id,
                'postId': post.post_id,
                'title': post.post_title,
                'content': post.post_content,
                'shareUrl': post.post_share_url,
                'authorId': post.post_author_id,
                'authorName': post_user.user_name if post_user else None,
                'authorAvatar': post_user.user_avatar if post_user else None,
                'category': post.post_category,
                'ip': post.post_ip,
                'likedCount': interact.liked_count if interact else '0',
                'collectedCount': interact.collected_count if interact else '0',
                'media': media.dict() if media else None,
                'tags': tags,
                'createdAt': datetime.strftime(post.created_at, '%Y-%m-%d %H:%M:%S'),
            }
            return send_success(data)
        except Exception as e:
            return send_server_error(str(e))

    @jwt_required()
    def delete(self, post_id):
        try:
            from ..models.post_media import PostMediaModel
            post = PostDetailModel.get_post_by_post_id(post_id)
            if not post:
                return send_error('笔记不存在')

            media = PostMediaModel.find_by_post_id(post_id)
            if media:
                PostMediaModel.delete(media)

            interact = PostInteractModel.find_by_post_id(post_id)
            if interact:
                PostInteractModel.delete(interact)

            PostDetailModel.delete(post)
            return send_success('删除成功')
        except Exception as e:
            return send_server_error(str(e))


class UserListResource(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('pageSize', type=int, default=20, location='args')
        parser.add_argument('keyword', type=str, default='', location='args')
        args = parser.parse_args()

        try:
            query = UserModel.query

            if args['keyword']:
                keyword = f'%{args["keyword"]}%'
                query = query.filter(UserModel.user_name.like(keyword))

            total = query.count()
            users = query.order_by(UserModel.created_at.desc()).offset(
                (args['page'] - 1) * args['pageSize']
            ).limit(args['pageSize']).all()

            items = [u.dict() for u in users]

            return send_success({
                'items': items,
                'total': total,
                'page': args['page'],
                'pageSize': args['pageSize'],
            })
        except Exception as e:
            return send_server_error(str(e))