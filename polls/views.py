from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from polls import final_project

def search(request):
    return render(request, 'search.html')

def result(request):
    stock_list = request.POST.getlist('stock')
    return render(request, 'result.html', {
        'value': final_project.func(stock_list),
    })
