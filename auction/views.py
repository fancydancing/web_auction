from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import Item
import time

def index(request):
    return HttpResponse("Hello, world. You're at the auction index.")

def show_items(request):
    return render(request, 'items.html')


# Create an item or get a list of items
def items(request):
    if request.method == 'POST':
        return add_item(request)
    else:
        page = request.POST.get('page')
        print(page)
        qs = Item.objects.order_by('-create_dt')

        items_list = [{
                   "id": item.id,
                   "title": item.title,
                   "description": item.description,
                   "create_dt": int(time.mktime(item.create_dt.timetuple())),
                   "close_dt": int(time.mktime(item.close_dt.timetuple())),
                   "start_bid": item.start_bid,
                   "price": item.price,
                   } for item in qs]

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
    item.close_dt = data.get('close_dt') or item.close_dt
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
    print(item)
    result = json.dumps(item)
    return HttpResponse(result, content_type="text/json")



# Updating and reading an item
def item_info(request, pk):
    if pk and pk != 'null':
        item = get_object_or_404(Item, pk=pk)
    else:
        return HttpResponse("Item is undefined")
    if request.method == 'PUT':
        print('----PUT----')
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
        return item_edit(data, item)
    elif request.method == 'DELETE':
        print('----DELETE----')
        return item_delete(item)
    elif request.method == 'GET':
        print('----GET----')
        return item_read(item)