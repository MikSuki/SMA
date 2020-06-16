from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
# from polls import crawler
import subprocess


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
        'value': runCrawler(cmd),
    })

def runCrawler(cmd):
    output = subprocess.check_output(cmd, shell=True)
    # print(str(output ))
    return str(output )

