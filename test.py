import urllib.request as req
import bs4
from requests_html import HTMLSession
import numpy
import multiprocessing as mp
from datetime import datetime 

def claw(stock_code):
    def find_root(url):  # 回傳網頁原始碼
        request = req.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        })
        with req.urlopen(request) as response:
            data = response.read().decode("utf-8")  # 預設就是utf-8
        root = bs4.BeautifulSoup(data, "html.parser")
        return root

    def click_btn(root, btn_name):  # 回傳按鈕連結網址
        # '\'為換行符號
        # find用法 https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/#find
        buttons = root.find("div", class_="wrap")\
            .find("nav", class_="primary navi-wrap")\
            .find("ul", class_="primary-navi")\
            .find_all("li")
        # for button in buttons:
        #     print(button.a.string)
        for button in buttons:
            if button.a.string == btn_name:
                return("https://www.cmoney.tw"+button.a["href"])
        return False

    def item_crawler(url, catch_name, title_posit, find_StoP):
        finded = False
        give5y = True
        session = HTMLSession()  # These sessions are for making HTTP requests:
        # https://requests-html.kennethreitz.org/#html-sessions
        r = session.get(url)  # r為request
        r.html.render(sleep=5)  # this call executes the js in the page
        # sleep 在頁面初次渲染之後的等待時間

        if find_StoP:
            StockPrice = r.html.find(
                'ul.s-infor-list', first=True).find('div.f-twenty', first=True)
            # first=True 只傳回第一個找到的元素
            js = r.html.find('div.tb-out', first=True)
            items = js.find('tr')
            items = items[1:len(items)]
            for i in range(5):
                datas = items[i].find('td')
                # print(datas[5].text)
                if datas[5].text == '0.00':
                    # print('hahaha')
                    give5y = False

        js = r.html.find('div.tb-out', first=True)  # first=True 只傳回第一個找到的元素
        # 有加first=True類似find,沒加類似find_all
        # print(js)

        items = js.find('tr')
        items = items[1:len(items)]
        # for item in items:
        #     print(item)
        item_names = js.find(title_posit)
        for item, item_name in zip(items, item_names):
            if item_name.text == catch_name:
                datas = item.find('td')
                finded = True
        if finded:
            # print(type(datas))
            datas = datas[1:len(datas)]
            list = []
            for data in datas:
                try:
                    list.append(float(data.text))
                except ValueError:
                    list.append(data.text)
            if(find_StoP):
                return float(StockPrice.text), list, give5y
            else:
                return list
            # 遠端主機已強制關閉一個現存的連線 https://blog.aidec.tw/post/python-requests-10054
        else:
            return False

    # btn_name=input('Input btn_name:')
    btn_name = '財務比率'
    item_name = '稅後股東權益報酬率'
    # while True:
    cnt = 0
    # stock_code = input('輸入股票代碼：')
    # if stock_code == "0":
    #     break
    stocklist = []
    roe = []
    price = []
    CashYield = []
    TotYield = []
    give5y = []
    ciratio = []

    stocklist.append(stock_code)
    url = general_url+stock_code
    root = find_root(url)

    new_page = click_btn(root, btn_name)
    roe.append(numpy.mean(item_crawler(
        new_page, item_name, 'td.align-left', 0)))
    print('股票代碼'+stock_code+'的roe:', roe[cnt])

    newpage = click_btn(root, '股利政策')
    yiel = []
    pri, yiel, g5 = (item_crawler(
        newpage, '2019', 'td.align-center', True))
    price.append(pri)
    CashYield.append(yiel[0]/pri)
    TotYield.append(yiel[4]/pri)
    give5y.append(g5)
    print('股票代碼'+stock_code+'的股價:', price[cnt])
    print('股票代碼'+stock_code+'的現金殖利率:', CashYield[cnt])
    print('股票代碼'+stock_code+'的總殖利率:', TotYield[cnt])
    print('是否連續5年發股:', '是' if give5y[cnt] else '否')

    new_page = click_btn(root, '本益比')
    cir = []
    cir = item_crawler(new_page, '2020Q1', 'td.align-center', 0)
    ciratio.append(cir[2])
    print('股票代碼'+stock_code+'的本益比:', ciratio[cnt])
    cnt = cnt+1


start_time = datetime.now() 
general_url = 'https://www.cmoney.tw/finance/f00043.aspx?s='
MAX_CPUS = mp.cpu_count()
stocks = [
    1101, 
    2330, 
    3006, 
    4104,
    5009, 
    6015,
    7402,
    8016
]
p_list = []

if __name__ == '__main__':  # 必須放這段代碼，不然會Error
    i = 0
    while i < len(stocks):
        n = MAX_CPUS
        if n > len(stocks) - i:
            n = len(stocks) - i
        for j in range(i, i + n):
            p = mp.Process(target=claw, args=(str(stocks[j]),))
            p.start()
            p_list.append(p)
            print(str(j) + ' start')
        for p in p_list:
            p.join()
        i += MAX_CPUS
        if i >= len(stocks): 
            break
        p_list = []
        print('next')

    # 開始加速執行
    # ap.start()
    # jk.start()

    # 結束多進程
    # ap.join()
    # jk.join()

    print('over')
    time_elapsed = datetime.now() - start_time 
    print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
