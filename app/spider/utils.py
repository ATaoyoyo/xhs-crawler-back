import re
from urllib.parse import urlparse
from .exceptions import InvalidURLException
from ..utils.logger import log


def extract_url(text):
    if not text:
        log.warning("提取URL失败: 输入文本为空")
        raise InvalidURLException("分享文本为空，无法提取URL")

    # 匹配URL的正则表达式
    # 改进版 URL 匹配正则
    url_pattern = r'((?:https?://)?(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?)'

    matches = re.findall(url_pattern, text)

    # 标准化：确保每个 URL 带有协议前缀
    urls = ['https://' + u if not u.startswith('http') else u for u in matches]
    if not urls:
        log.warning(f"提取URL失败: 未在文本中找到URL: {text[:100]}...")
        raise InvalidURLException("未在分享文本中找到有效URL")

    # 返回第一个匹配的URL
    url = urls[0]
    log.debug(f"成功提取URL: {url}")
    return url


def validate_xhs_url(url):
    if not url:
        return False

    try:
        parsed_url = urlparse(url)
        # 检查域名是否为小红书相关域名
        valid_domains = ['xiaohongshu.com', 'xhslink.com', 'xhslink.cn', 'xhs.cn']
        return any(domain in parsed_url.netloc for domain in valid_domains)
    except Exception as e:
        log.error(f"URL验证异常: {e}")
        return False



