from flask_restful import Resource, reqparse
from app.spider.scheduler import spider_scheduler
from app.utils.logger import log

from ..models.post_detail import PostDetailModel
from ..models.post_media import PostMediaModel
from ..models.post_tag import PostTagModel
from ..models.post_user import PostUserModel
from ..models.post_interact import PostInteractModel

from ..response import send_success, send_error, send_server_error


class SpiderListAPI(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, location='json')
        args = parser.parse_args()

        try:
            if not args['content']:
                log.warning('SpiderListAPI POST 参数错误')
                return send_error('参数错误!')

            post_id = spider_scheduler.run_spider_sync(spider_name='post_media_spider', params=args)

            post_detail = PostDetailModel.get_post_by_post_id(post_id)
            post_media = PostMediaModel.find_by_post_id(post_id)
            post_user = PostUserModel.find_by_user_id(post_detail.post_author_id)
            post_interact = PostInteractModel.find_by_post_id(post_id)

            post_tag = []
            for tag in post_detail.dict().get('tagsId'):
                t = PostTagModel.find_by_tag_id(tag)
                post_tag.append(t.dict())

            log.info('SpiderListAPI POST 成功!')
            data = {
                'detail': post_detail.dict(),
                'media': post_media.dict(),
                'user': post_user.dict(),
                'interact': post_interact.dict(),
                'tags': post_tag
            }
            return send_success(data=data)
        except Exception as e:
            return send_server_error(message=str(e))

    def get(self):
        post = PostDetailModel.get_all_posts()

        try:
            post_list = []
            if post:
                for post_detail in post:
                    post_list.append(post_detail.dict())
            return send_success(data=post_list)
        except Exception as e:
            return send_server_error(message=str(e), exception=e)


class SpiderDetailAPI(Resource):
    def get(self, post_id):
        try:
            post = PostDetailModel.get_post_by_post_id(post_id)

            if post:
                media = PostMediaModel.find_by_post_id(post_id)
                user = PostUserModel.find_by_user_id(post.post_author_id)
                interact = PostInteractModel.find_by_post_id(post_id)

                tags = []
                for tag in post.dict().get('tagsId'):
                    t = PostTagModel.find_by_tag_id(tag)
                    tags.append(t.dict())

                data = {
                    'post': post.dict(),
                    'media': media.dict(),
                    'user': user.dict(),
                    'interact': interact.dict(),
                    'tags': tags
                }
                return send_success(data=data)
            else:
                return send_error('没有查询到该笔记')
        except Exception as e:
            return send_server_error(message=str(e), exception=e)

    def delete(self, post_id):
        try:
            post_detail = PostDetailModel.get_post_by_post_id(post_id)

            if post_detail:
                post_media = PostMediaModel.find_by_post_id(post_id)
                PostMediaModel.delete(post_media)
                post_interact = PostInteractModel.find_by_post_id(post_id)
                PostInteractModel.delete(post_interact)
                PostDetailModel.delete(post_detail)
                return send_success('删除成功')
            else:
                return send_error('没有找到该笔记!')

        except Exception as e:
            return send_server_error(message=str(e), exception=e)
