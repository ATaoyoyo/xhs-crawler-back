from dataclasses import dataclass
from typing import List


@dataclass
class PostDetailItem:
    """
    笔记信息
    """
    post_id: str
    post_title: str
    post_content: str
    post_share_url: str
    post_date: str
    post_updated: str
    post_author_id: str
    post_at_user_id: str
    post_category: str
    post_tags_id: str
    post_ip: str

    def dict(self):
        return {**self.__dict__}


@dataclass
class PostMediaItem:
    """
    笔记图片信息
    """
    post_id: str
    post_images: str
    post_videos: str

    def dict(self):
        return {**self.__dict__}


@dataclass
class PostTagItem:
    """
    笔记标签信息
    """
    tag_id: str
    tag_name: str
    tag_type: str
    tag_count: int

    def dict(self):
        return {**self.__dict__}


@dataclass
class PostUserItem:
    """
    笔记用户信息
    """
    user_id: str
    user_name: str
    user_avatar: str
    user_xsec_token: str

    def dict(self):
        return {**self.__dict__}


@dataclass
class PostInteractItem:
    """
    笔记互动信息
    """
    post_id: str
    collected_count: str
    comment_count: str
    share_count: str
    liked_count: str

    def dict(self):
        return {**self.__dict__}
