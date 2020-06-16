import json
import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner, CrawlerProcess
import urllib.parse
import sys

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'https://www.cmoney.tw/finance/f00025.aspx?s=6215',
    ]

    def parse(self, response):
        global CMKEY
        # print('cmkey -------------------- \n')
        CMKEY = response.xpath(
            '//a[@href="/finance/f00042.aspx?s=6215"]/@cmkey').extract()[0]
        CMKEY = urllib.parse.quote(CMKEY)  # encode url
        # print(CMKEY + '\n------------------------------ ')


class QuotesSpider2(scrapy.Spider):
    name = "quotes2"

    def __init__(self):
        self.headers = {
            'Host': 'www.cmoney.tw',
            'Referer': 'https://www.cmoney.tw/finance/f00042.aspx?s=6215',
        }

    def start_requests(self):
        global CMKEY, urls

        for url in urls:
            yield scrapy.Request(
                url=url + CMKEY,
                headers=self.headers,
                callback=self.parse
            )

    def parse(self, response):
        data.append(response.body.decode(encoding='UTF-8',))


CMKEY = ''
data = []
url_0 = 'https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetStockListLatestSaleData&stockId='
url_1 = '&cmkey='
urls = []


def craw(stock_list):
    data_obj = {}
    # create urls
    for stock_id in stock_list:
        urls.append(url_0 + str(stock_id) + url_1)

    runner = CrawlerRunner()

    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(QuotesSpider)
        yield runner.crawl(QuotesSpider2)
        reactor.stop()

    crawl()
    reactor.run()  # the script will block here until the last crawl call is finished
    print(data)

craw(sys.argv[1:])
