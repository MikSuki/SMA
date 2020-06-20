import json
import scrapy
from twisted.internet import reactor, defer  # 管理事件驅動
from scrapy.crawler import CrawlerRunner, CrawlerProcess
import urllib.parse
import sys
import pandas as pd


class QuotesSpider(scrapy.Spider):
    global key_tag
    name = "quotes"
    start_urls = [
        'https://www.cmoney.tw/finance/f00027.aspx?s=6215',
    ]

    def parse(self, response):
        global CMKEY
        # print(response.text)
        # print('cmkey -------------------- \n')

        CMKEY = response.xpath(  # 獲得cmkey
            '//a[@href="/finance/f00027.aspx?s=6215"]/@cmkey').extract()[0]
        CMKEY = urllib.parse.quote(CMKEY)  # 解碼cmkey
        # print(CMKEY + '\n------------------------------ ')


class QuotesSpider2(scrapy.Spider):
    name = "quotes2"
    # global key_tag

    def __init__(self):
        global key_tag
        # print(key_tag)
        self.headers = {
            'Host': 'www.cmoney.tw',
            'Referer': 'https://www.cmoney.tw/finance/f00027.aspx?s=6215',
        }

    def start_requests(self):
        global CMKEY, urls

        for url in urls:
            yield scrapy.Request(
                # 非同步 https://medium.com/%E9%AB%92%E6%A1%B6%E5%AD%90/aysnc-await-%E6%95%99%E5%AD%B8%E7%AD%86%E8%A8%98-debabdb9db0e
                url=url + CMKEY,
                headers=self.headers,
                callback=self.parse
            )

    def parse(self, response):
        data.append(response.body.decode(encoding='UTF-8',))
        # print(type(response.body.decode(encoding='UTF-8',)))
        # print(response)


def analysis(data, stock_list):
    def push(arr, v):
        try:
            arr.append(float(v))
        except ValueError:
            arr.append(float(-999999))

    SalePr = []
    SaleQty = []
    roe = []
    PERByTWSE = []
    CashYield = []
    TotYield = []
    give5y = []

    for i in range(len(data)):
        if(type(eval(data[i])) is dict):
            common_info = eval(data[i])
            SalePr.append(float((common_info["commSaleData"])["SalePr"]))
            SaleQty.append(float((common_info["commSaleData"])["SaleQty"]))

    cnt = 0
    cnt2 = 0
    for i in range(len(data)):
        if(type(eval(data[i])) is list):
            data_tr = eval(data[i])
            if('SeasonDate' in data_tr[0]):  # 本益比
                push(PERByTWSE, data_tr[0]["PERByTWSE"])
            if('Date' in data_tr[0]):  # 股利政策
                give5y_b = True
                for i in range(5):
                    if(float(data_tr[0]["TotalDividend"]) == 0):
                        give5y_b = False
                        break
                give5y.append(give5y_b)
                CashYield.append(float(data_tr[0]["CashDividend"])/SalePr[cnt])
                TotYield.append(float(data_tr[0]["TotalDividend"])/SalePr[cnt])
                cnt = cnt+1

            if('DateRange' in data_tr[0]):  # 財務比率
                roe.append(float(data_tr[0]["ROE"])+float(data_tr[1]["ROE"]) +
                           float(data_tr[2]["ROE"])+float(data_tr[3]["ROE"]))

    return SalePr, SaleQty, roe, PERByTWSE, CashYield, TotYield, give5y

def match_cond(SalePr, SaleQty, roe, PERByTWSE, CashYield, TotYield, give5y):
    cnt = len(SalePr)
    proper = []
    for i in range(cnt):
        if(SaleQty[i] > 1500 and SalePr[i] <= 100 and (CashYield[i] >= 0.03
                                                       or TotYield[i] >= 0.05) and give5y[i] and PERByTWSE[i] <= 20):
            if((SaleQty[i] < 5000 and roe[i] >= 7) or (SaleQty[i] > 5000 and roe[i] >= 6)):
                # print(stocklist[i],'適合存股')
                proper.append(True)
            else:
                # print(stocklist[i],'不適合存股')
                proper.append(False)
        else:
            # print(stocklist[i],'不適合存股')
            proper.append(False)
    return proper

def to_json2(df, orient='split'):
    df_json = df.to_json(orient=orient, force_ascii=False)
    return json.loads(df_json)

def start(stock_list):
    data_obj = {}
    stock_info = {}
    runner = CrawlerRunner()
    # print(len(stock_list))

    @defer.inlineCallbacks
    def crawl():
        global key_tag
        yield runner.crawl(QuotesSpider)
        for stock_id in stock_list:
            urls[0] = (url_0_0 + str(stock_id) + url_1)
            urls[1] = (url_0_1 + str(stock_id) + url_1)
            urls[2] = (url_0_2 + str(stock_id) + url_1)
            urls[3] = (url_0_3 + str(stock_id) + url_1)
            yield runner.crawl(QuotesSpider2)
        reactor.stop()
    crawl()
    reactor.run()  # the script will block here until the last crawl call is finished

    SalePr = []
    SaleQty = []
    roe = []
    PERByTWSE = []
    CashYield = []
    TotYield = []
    give5y = []
    [SalePr, SaleQty, roe, PERByTWSE, CashYield,
        TotYield, give5y] = analysis(data, stock_list)
    stock_info["股價"] = SalePr
    stock_info["成交量"] = SaleQty
    stock_info["ROE"] = roe
    stock_info["本益比"] = PERByTWSE
    stock_info["現金殖利率"] = CashYield
    stock_info["總殖利率"] = TotYield
    stock_info["是否連續5年配股"] = give5y
    prefer = []
    prefer = match_cond(SalePr, SaleQty, roe, PERByTWSE,
                        CashYield, TotYield, give5y)
    # print("股票",stock_id)
    # print(stock_info)

    obj = {}
    STOCK_INFO_NAME = [
        "股價",
        "成交量",
        "ROE",
        "本益比",
        "現金殖利率",
        "總殖利率",
        "是否連續5年配股"
    ]
    for i in range(len(stock_list)):
        arr = []
        arr.append(stock_list[i])
        for j in range(len(STOCK_INFO_NAME)):
            arr.append(str(stock_info[STOCK_INFO_NAME[j]][i]))
        arr.append(str(prefer[i]))
        obj[str(i)] = arr
    print(obj)


CMKEY = []
data = []
url_0_0 = 'https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetStockListLatestSaleData&stockId='  # 首頁
url_0_1 = 'https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetFinancialRatios&stockId='  # 財務比率
url_0_2 = 'https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetDividendPolicy&stockId='  # 股利政策
url_0_3 = 'https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetPERAndEPSBySeason&stockId='  # 本益比
url_1 = '&selectedType=4&cmkey='
urls = ['', '', '', '']


start(sys.argv[1:])
# 2892,2891,2882
