import json


def func(stock_list):
    obj= {}
    for i in range(len(stock_list)):
        obj[str(i)] = stock_list[i]
    return json.dumps(obj)
