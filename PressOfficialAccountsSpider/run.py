from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from press.spiders.press_spider import PressSpider
from twisted.internet import reactor

if __name__ == '__main__':
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)
    runner.crawl(PressSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()  # the script will block here until all crawling jobs are finished