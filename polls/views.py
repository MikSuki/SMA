from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from polls import final_project


def search(request):
    f = open("data/stock_list.json", "r", encoding="utf-8")
    data = f.read()
    f.close()
    return render(request, 'search.html', {
        'value': data
    })


def result(request):
    stock_list = request.POST.getlist('stock')
    return render(request, 'result.html', {
        'value': final_project.func(stock_list),
    })
