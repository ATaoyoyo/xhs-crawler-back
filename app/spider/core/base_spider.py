from abc import ABC, abstractmethod
import requests
from app.utils.logger import log
from ..exceptions import ResourceNotFoundException, NetworkException


class BaseSpider(ABC):
    def __init__(self, params=None):
        self.params = params or {}
        self.pipelines = []

    @abstractmethod
    def start_requests(self):
        pass

    @abstractmethod
    def parse(self, response):
        pass

    def process_item(self, item):
        processed = item
        for pipeline in self.pipelines:
            processed = pipeline.process(processed)
            if processed is None:
                return None
        return processed

    def add_pipeline(self, pipeline):
        """添加数据处理管道"""
        self.pipelines.append(pipeline)

    def run(self):
        request = self.start_requests()
        response = self.download(request)

        text = response.get('text')
        url = response.get('url')
        data = self.parse(text)
        processed = self.process_item({'url': url, 'data': data})
        return processed

    def download(self, request):
        response = requests.get(request.get('url'), headers=request.get('headers'), timeout=request.get('timeout'))
        if response.status_code != 200:
            log.warning(f'请求返回非200状态码: {response.status_code}, URL: {request.get("url")}')

            if response.status_code == 404:
                raise ResourceNotFoundException(f'页面不存在: {request.get("url")}')
            else:
                raise NetworkException(f'网络请求失败: {request.get("url")}')
        log.debug(f"成功获取页面，长度: {len(response.text)}字节")
        return {
            "text": response.text,
            "url": request.get("url"),
        }
