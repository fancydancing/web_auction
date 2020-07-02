from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.db.models import Q
import json
from .models import Item, Bid
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
        print(request)
        # data = json.loads(request.body.decode('utf-8'))
        page_number = request.GET['page']
        sort = request.GET['sort']
        order = request.GET['order']
        search_string = request.GET['search_string']

        items_qs = Item.objects.all()
        if search_string != 'null':
            items_qs = items_qs.filter(Q(title__icontains=search_string) |
                                       Q(description__icontains=search_string))

        if sort != 'null':
            sorting_column = sort if order == 'asc' else '-' + sort
            items_qs = items_qs.order_by(sorting_column)

        total_count = items_qs.count()
        if page_number:
            paginator = Paginator(items_qs, 10)  # Show 10 items per page.
            inverted_page = paginator.num_pages - int(page_number) - 1  # Zero page in Django is the last for the interface
            items_qs = paginator.get_page(inverted_page).object_list
            print(items_qs)

        items_list = {'items': [{
                        "id": item.id,
                        "title": item.title,
                        "description": item.description,
                        "create_dt": to_epoch(item.create_dt),
                        "close_dt": to_epoch(item.close_dt),
                        "start_bid": item.start_bid,
                        "price": item.price,
                        } for item in items_qs],
                      'total_count': total_count
                     }

        items_json = json.dumps(items_list, cls=DjangoJSONEncoder)

        return HttpResponse(items_json, content_type="text/json")

# Create an item
def add_item(request):
    data = json.loads(request.body.decode('utf-8'))
    data['close_dt'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['close_dt']))
    new_item = Item.objects.create(**data)

    context = {"id": new_item.id}
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
        data = json.loads(request.body.decode('utf-8'))
        return item_edit(data, item)
    elif request.method == 'DELETE':
        return item_delete(item)
    elif request.method == 'GET':
        return item_read(item)


# Logging in
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

# List of bids for an item
def get_bids(pk):
    bids_qs = Bid.objects.filter(item_id=pk).order_by('-bid_dt')

    bids_list = [{
        "id": bid.id,
        "bid_dt": to_epoch(bid.bid_dt),
        "price": bid.price,
        "user_name": bid.user_name
    } for bid in bids_qs]

    bids_json = json.dumps(bids_list, cls=DjangoJSONEncoder)
    return HttpResponse(bids_json, content_type="text/json")

def set_bid(data, pk):
    item = get_object_or_404(Item, pk=pk)
    data['item_id'] = item
    price = data('price')
    user_name = data('user_name')

    if price <= item.price:
        return HttpResponse('You have to make a higher bid')

    bids_qs = get_bids(pk)
    highest_bid = bids_qs[0]

    if user_name == highest_bid.user_name:
        return HttpResponse('Your bid is already the highest')

    new_bid = Bid.objects.create(**data)
    context = {"id": new_bid.id}
    return HttpResponse(json.dumps(context), content_type="text/json")


# Reading and setting bids for an item
def item_bids(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        return set_bid(data, pk)
    elif request.method == 'GET':
        return get_bids(pk)
