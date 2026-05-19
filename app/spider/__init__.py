from .core.post_media_spider import PostMediaSpider

# 爬虫注册
spider_register = {
    PostMediaSpider.name: PostMediaSpider
}


def get_spider_class(name):
    return spider_register.get(name)
