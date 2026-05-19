from . import get_spider_class


class SpiderScheduler:

    def run_spider_sync(self, spider_name, params=None):
        spider_cls = get_spider_class(spider_name)

        if not spider_cls:
            raise ValueError(f"Spider {spider_name} not found")

        try:
            spider = spider_cls(params)
            results = spider.run()
            return results

        except Exception as e:
            raise e


spider_scheduler = SpiderScheduler()


def init_scheduler(app):
    spider_scheduler.app = app
