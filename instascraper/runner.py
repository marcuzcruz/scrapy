from sys import argv

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instascraper.spiders.instagram import InstagramSpider
from instascraper import settings

if __name__ == '__main__':
    if len(argv[1:]) < 3:
        exit(1)

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, login=argv[1], encrypted_pwd=argv[2].strip(), users_to_scrape=argv[3:])
    process.start()
