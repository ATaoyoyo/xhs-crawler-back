import json

from bs4 import BeautifulSoup

from .base_spider import BaseSpider
from ..utils import extract_url, validate_xhs_url
from ..config import REQUEST_CONFIG
from ..exceptions import ResourceNotFoundException, ContentParsingException
from ..pipelines import PostCleaningPipeline, PostDatabasePipeline
from app.utils.logger import log


class PostMediaSpider(BaseSpider):
    name = 'post_media_spider'

    def __init__(self, params=None):
        super().__init__(params)

        self.add_pipeline(PostCleaningPipeline())
        self.add_pipeline(PostDatabasePipeline())

    def start_requests(self):
        content_text = self.params.get('content')

        url = extract_url(content_text)

        if not url:
            raise ValueError('没有提取到有效的url地址')

        if not validate_xhs_url(url):
            raise ValueError('提供的不是有效的小红书链接')

        headers = REQUEST_CONFIG.get('headers')
        return {'url': url, 'headers': headers, 'timeout': REQUEST_CONFIG.get('timeout')}

    def parse(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        page_data = None

        for script in soup.find_all('script'):
            if "window.__INITIAL_STATE__=" not in script.get_text():
                continue

            json_str = script.get_text().split('window.__INITIAL_STATE__=')[1]
            json_str = json_str.replace("undefined", '""').replace("\u002F", "/")

            try:
                page_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                log.error(f"JSON解析失败: {str(e)}")
                raise ContentParsingException(f"数据解析失败或笔记不存在: {str(e)}")

        if not page_data:
            log.warning('页面不存在或已删除')
            raise ResourceNotFoundException('笔记不存在或已被删除')
        return {'data': page_data}

    # def process_item(self, item):
    #     return item
