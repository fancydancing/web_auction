from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import Item
import time

def show_items(request):
    return render(request, 'items.html')

def to_epoch(value):
    return int(time.mktime(value.timetuple()))

def from_epoch(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))

# Create an item or get a list of items
def items(request):
    if request.method == 'POST':
        return add_item(request)
    else:
        page = request.POST.get('page')
        qs = Item.objects.order_by('-create_dt')

        items_list = {'items': [{
                        "id": item.id,
                        "title": item.title,
                        "description": item.description,
                        "create_dt": to_epoch(item.create_dt),
                        "close_dt": to_epoch(item.close_dt),
                        "start_bid": item.start_bid,
                        "price": item.price,
                        } for item in qs],
                      'total_count': qs.count()
                     }

        items_json = json.dumps(items_list, cls=DjangoJSONEncoder)

        return HttpResponse(items_json, content_type="text/json")

# Create an item
def add_item(request):

    data = json.loads(request.body.decode('utf-8'))
    data['close_dt'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))
    new_item = Item.objects.create(**data)

    context = {"newID": new_item.id}
    return HttpResponse(json.dumps(context), content_type="text/json")

# Item editing
def item_edit(data, item):
    item.title = data.get('title') or item.title
    item.description = data.get('description') or item.description
    item.price = data.get('price') or item.price
    item.close_dt = from_epoch(data.get('close_dt')) or item.close_dt
    item.save()

    result = {"result": True}
    return HttpResponse(result, content_type="text/json")

# Item deleting
def item_delete(item):
    item.delete()
    result = {"result": True}
    return HttpResponse(result, content_type="text/json")

# Item reading
def item_read(item):
    result = {'id': item.id,
              'title': item.title,
              'description': item.description,
              'create_dt': to_epoch(item.create_dt),
              'close_dt': to_epoch(item.close_dt),
              'price': item.price
             }
    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type="text/json")

# Updating and reading an item
def item_info(request, pk):
    if pk and pk != 'null':
        item = get_object_or_404(Item, pk=pk)
    else:
        return HttpResponse("Item is undefined")
    if request.method == 'PUT':
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
        return item_edit(data, item)
    elif request.method == 'DELETE':
        return item_delete(item)
    elif request.method == 'GET':
        return item_read(item)


def sign_in(request):
    login_pass = {'admin': 'admin',
                  'user': 'user',
                  'user2': 'user2'}

    data = json.loads(request.body.decode('utf-8'))
    username = data.get('login')
    password = data.get('password')

    if username not in login_pass.keys() or password != login_pass[username]:
        res = False
        role = None
    else:
        res = True
        role = 'admin' if username == 'admin' else 'user'

    result = {'result': res, 'login': username, 'role': role}
    return HttpResponse(json.dumps(result), content_type="text/json")
