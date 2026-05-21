from datetime import datetime

from .items import PostDetailItem, PostMediaItem, PostUserItem, PostTagItem, PostInteractItem
from app.api.models.post_detail import PostDetailModel
from app.api.models.post_media import PostMediaModel
from app.api.models.post_tag import PostTagModel
from app.api.models.post_interact import PostInteractModel
from app.api.models.post_user import PostUserModel
from app.api.models.post_detail_tag import PostDetailTagModel
from app.utils.logger import log
from app.utils.download import download_media


class PostCleaningPipeline:
    def process(self, item):
        data = item.get("data")
        url = item.get("url")
        note = data.get('data').get('note')
        note_id = note.get('currentNoteId')
        note_detail = note.get('noteDetailMap').get(note_id).get('note')

        log.info(f'开始处理数据: {note_detail.get("title")}')

        post_detail = self.detail_info(note_id, url, note_detail)
        post_media = self.media_info(note_id, note_detail)
        post_tag = self.tag_info(note_detail)
        post_user = self.user_info(note_detail)
        post_interact = self.interact_info(note_id, note_detail)

        log.info(f'处理完成: {note_detail.get("title")}')

        return {
            "post_id": note_id,
            "post_detail": post_detail,
            "post_media": post_media,
            "post_tag": post_tag,
            "post_user": post_user,
            "post_interact": post_interact
        }

    def detail_info(self, note_id, url, note_detail):
        pub_time = note_detail.get('time')
        update_time = note_detail.get('lastUpdateTime')
        tags_id = []
        for tag in note_detail.get('tagList'):
            tags_id.append(tag.get('id'))

        at_users_id = []
        for at in note_detail.get('atUserList'):
            at_users_id.append(at.get('userId'))

        return PostDetailItem(
            post_id=note_id,
            post_title=note_detail.get('title'),
            post_share_url=url,
            post_date=datetime.fromtimestamp(pub_time / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            post_updated=datetime.fromtimestamp(update_time / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            post_content=note_detail.get('desc'),
            post_author_id=note_detail.get('user').get('userId'),
            post_at_user_id=','.join(at_users_id),
            post_category=note_detail.get('type'),
            post_tags_id=','.join(tags_id),
            post_ip=note_detail.get('ipLocation'),
        ).dict()

    def media_info(self, note_id, note_detail):
        images = []
        videos = []
        for media_item in note_detail.get('imageList'):
            images.append(media_item.get('urlDefault'))
            stream = media_item.get('stream')
            # 实况图视频
            if stream:
                for key, value in stream.items():
                    if len(value) > 0:
                        for video_item in value:
                            videos.append(video_item.get('masterUrl'))
        #   视频笔记
        if note_detail.get('type') == 'video':
            video_list = note_detail.get('video').get('media').get('stream').get('h264')
            for video in video_list:
                videos.append(video.get('masterUrl'))

        # 下载媒体到本地
        download_media(note_id, [*images, *videos])

        return PostMediaItem(
            post_id=note_id,
            post_images=','.join(images),
            post_videos=','.join(videos)
        ).dict()

    def user_info(self, note_detail):
        user = note_detail.get('user')
        return PostUserItem(
            user_id=user.get('userId'),
            user_name=user.get('nickname'),
            user_avatar=user.get('avatar'),
            user_xsec_token=user.get('xsecToken')
        ).dict()

    def tag_info(self, note_detail):
        tag = []
        for tag_item in note_detail.get('tagList'):
            tag.append(PostTagItem(
                tag_id=tag_item.get('id'),
                tag_name=tag_item.get('name'),
                tag_type=tag_item.get('type'),
                tag_count=1
            ).dict())
        return tag

    def interact_info(self, note_id, note_detail):
        interact = note_detail.get('interactInfo')
        return PostInteractItem(
            post_id=note_id,
            collected_count=interact.get('collectedCount'),
            comment_count=interact.get('commentCount'),
            share_count=interact.get('shareCount'),
            liked_count=interact.get('likedCount')
        ).dict()


class PostDatabasePipeline:
    def process(self, item):
        log.info('开始保存数据')
        post_id = item.get('post_detail').get('post_id')
        exits = PostDetailModel.get_post_by_post_id(post_id)
        tag_ids = [tag.get('tag_id') for tag in item.get('post_tag')]

        if exits:
            log.info('笔记已经存在')
            log.info(f'更新数据库笔记: {exits.post_title}: ')

            media = PostMediaModel.find_by_post_id(post_id)
            interact = PostInteractModel.find_by_post_id(post_id)

            exits.update(**item.get('post_detail'))
            media.update(**item.get('post_media'))
            interact.update(**item.get('post_interact'))

            self._sync_post_tags(post_id, tag_ids)

            log.success(f'笔记 {exits.post_title} 更新完毕!')
        else:
            PostDetailModel.add(**item.get('post_detail'))
            PostMediaModel.add(**item.get('post_media'))
            PostInteractModel.add(**item.get('post_interact'))

            if PostUserModel.find_by_user_id(item.get('post_user').get('user_id')) is None:
                PostUserModel.add(**item.get('post_user'))

            for tag in item.get('post_tag'):
                tag_info = PostTagModel.find_by_tag_id(tag.get('tag_id'))
                if tag_info:
                    tag_info.tag_count += 1
                    PostTagModel.update(tag_info)
                else:
                    PostTagModel.add(**tag)

            for tag_id in tag_ids:
                PostDetailTagModel.add(post_id=post_id, tag_id=tag_id)
            db.session.commit()

            log.info('保存完成')
        return item.get('post_id')

    def _sync_post_tags(self, post_id, tag_ids):
        PostDetailTagModel.delete_by_post_id(post_id)
        for tag_id in tag_ids:
            PostDetailTagModel.add(post_id=post_id, tag_id=tag_id)
        db.session.commit()
