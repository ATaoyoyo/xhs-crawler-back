class ScraperException(Exception):
    """爬虫基础异常类"""
    def __init__(self, message="爬虫操作异常", code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NetworkException(ScraperException):
    """网络请求异常"""
    def __init__(self, message="网络请求失败", code=503):
        super().__init__(message, code)


class ContentParsingException(ScraperException):
    """内容解析异常"""
    def __init__(self, message="内容解析失败", code=500):
        super().__init__(message, code)


class ResourceNotFoundException(ScraperException):
    """资源不存在异常"""
    def __init__(self, message="资源不存在或已删除", code=404):
        super().__init__(message, code)


class DownloadException(ScraperException):
    """下载异常"""
    def __init__(self, message="资源下载失败", code=500):
        super().__init__(message, code)


class InvalidURLException(ScraperException):
    """无效URL异常"""
    def __init__(self, message="无效的URL地址", code=400):
        super().__init__(message, code)