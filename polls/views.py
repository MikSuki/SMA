from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
# from polls import crawler
import subprocess
import json


def search(request):
    f = open("data/stock_list.json", "r", encoding="utf-8")
    data = f.read()
    f.close()
    return render(request, 'search.html', {
        'value': data
    })


def result(request):
    stock_list = request.POST.getlist('stock')

    cmd = ['python', 'polls/crawler.py']
    for s in stock_list:
        print(s)
        cmd.append(s)
    print(cmd)
    return render(request, 'result.html', {
        # 'value': '{"0": ["2330", "314.5", "47828.0", "24.82", "20.6", "0.030206677265500796", "0.030206677265500796", "True", "False"], "1": ["1101", "42.55", "25106.0", "12.370000000000001", "9.2", "0.058754406580493544", "0.07050528789659224", "True", "True"]}'
        'value': runCrawler(cmd),
    })


def runCrawler(cmd):
    output = ''
    try:
        output = subprocess.check_output(cmd, shell=True)
    except:
        return ''
    output = output.decode("utf-8").replace('\n','').replace('\r', '').replace("'", "\"")
    print(json.dumps(json.loads(output)))
    return json.dumps(json.loads(output))
