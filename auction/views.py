import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from . import utils
from .models import Item, Bid



def index_view(request):
    """Show start page with items list"""
    return render(request, 'items.html')


def items_view(request):
    """
    Operations with items depending on HTTP method.

    POST: add new item
    GET: return a list of all items
    """
    if request.method == 'POST':
        return add_item(request)
    else:
        return items_list(request)


def items_list(request):
    """
    Return a list of items.

    request parameters:
    [page] - number of page
    [sort] - 'asc' or 'desc'
    [order] - field name to sort on
    [search_string] - string to find in title or description
    [show_closed] - show closed items or not
    """
    page_number = request.GET.get('page', 0)
    sort = request.GET.get('sort', 'create_dt')
    order = request.GET.get('order', 'asc')
    search_string = request.GET.get('search_string', None)
    show_closed = request.GET.get('show_closed', False)

    items_qs = Item.objects.all()
    if search_string:
        items_qs = items_qs.filter(
            Q(title__icontains=search_string) |
            Q(description__icontains=search_string)
        )

    if not show_closed:
        items_qs = items_qs.filter(close_dt__lt=timezone.now())

    if sort:
        sorting_column = sort if order == 'asc' else '-' + sort
        items_qs = items_qs.order_by(sorting_column)

    total_count = items_qs.count()
    if page_number:
        paginator = Paginator(items_qs, 10)  # Show 10 items per page
        # Zero page in Django is the last for the interface
        inverted_page = paginator.num_pages - int(page_number) - 1
        items_qs = paginator.get_page(inverted_page).object_list

    items_list = {
        'items':
        [{
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "create_dt": utils.to_epoch(item.create_dt),
            "close_dt": utils.to_epoch(item.close_dt),
            "price": item.price,
        } for item in items_qs],
        'total_count': total_count
    }
    items_json = json.dumps(items_list, cls=DjangoJSONEncoder)
    return HttpResponse(items_json, content_type="text/json")


def add_item(request):
    """
    Create new item.

    request parameters:
    [title] - item title
    [description] - item description
    [close_dt] - closing time for bids
    [price] - item start price
    """

    data = json.loads(request.body.decode('utf-8'))
    data['close_dt'] = utils.from_epoch(data['close_dt'])

    params = ['title', 'description', 'close_dt', 'price']
    missing_params = [p for p in params if p not in data]
    if len(missing_params) > 0:
        result = {'result': False, 'msg': 'Missing parameters: ' + ', '.join(missing_params)}
        return HttpResponse(json.dumps(result), content_type="text/json")

    new_item = Item.objects.create(**data)

    result = {'result': True, 'id': new_item.id}
    return HttpResponse(json.dumps(result), content_type="text/json")


def item_edit(data, item):
    """
    Edit an item.

    parameters in data:
    [title] - item title
    [description] - item description
    [close_dt] - closing time for bids
    [price] - item start price
    """

    item.title = data.get('title', item.title)
    item.description = data.get('description', item.description)
    item.price = data.get('price', item.price)
    item.close_dt = utils.from_epoch(data.get('close_dt'), item.close_dt)
    item.save()

    result = {"result": True}
    return HttpResponse(json.dumps(result), content_type="text/json")


def item_delete(item):
    """Delete an item"""
    item.delete()
    result = {"result": True}
    return HttpResponse(result, content_type="text/json")


def item_read(item):
    """Read an item"""
    result = {
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'create_dt': utils.to_epoch(item.create_dt),
        'close_dt': utils.to_epoch(item.close_dt),
        'price': item.price
    }

    return HttpResponse(
        json.dumps(result, cls=DjangoJSONEncoder),
        content_type="text/json"
    )


def item_info_view(request, pk):
    """
    Operations with an existing item depending on HTTP method.

    PUT: update item
    DELETE: delete item
    GET: read item
    """
    if pk and pk != 'null':
        item = get_object_or_404(Item, pk=pk)
        if not item:
            return HttpResponse("Item is undefined")
    else:
        return HttpResponse("Item is undefined")
    # Edit item
    if request.method == 'PUT':
        data = json.loads(request.body.decode('utf-8'))
        return item_edit(data, item)
    # Delete item
    elif request.method == 'DELETE':
        return item_delete(item)
    # Read item
    elif request.method == 'GET':
        return item_read(item)


def sign_in_view(request):
    """Authorize user and return role and username.

    request parameters:
    [login]
    [password]
    """
    # Users allowed to login
    login_pass = {'admin': 'admin',
                  'user': 'user',
                  'user2': 'user2'}

    data = json.loads(request.body.decode('utf-8'))
    username = data.get('login')
    password = data.get('password')

    # Login/password check
    if username not in login_pass.keys() or password != login_pass[username]:
        res = False
        role = None
    else:
        res = True
        role = 'admin' if username == 'admin' else 'user'

    result = {'result': res, 'login': username, 'role': role}
    return HttpResponse(json.dumps(result), content_type="text/json")


def get_bids(item):
    """Get bids list for an item."""
    bids_qs = Bid.objects.filter(item_id=item).order_by('-bid_dt')

    bids_list = [{
        "id": bid.id,
        "bid_dt": utils.to_epoch(bid.bid_dt),
        "price": bid.price,
        "user_name": bid.user_name
    } for bid in bids_qs]

    bids_json = json.dumps(bids_list, cls=DjangoJSONEncoder)
    return HttpResponse(bids_json, content_type="text/json")


def set_bid(data, item):
    """
    Set a bid for an item.

    [item] - instance of Item
    parameters in data:
    [price] - bid value
    [user_name] - user making a bid
    """

    if item.close_dt <= timezone.now():
        result = {'result': False, 'msg': 'Sorry, this lot is already closed.'}
        return HttpResponse(json.dumps(result), content_type="text/json")

    # Validate parameters
    if 'price' not in data:
        result = {'result': False, 'msg': 'Price is required.'}
        return HttpResponse(json.dumps(result), content_type="text/json")
    price = int(data.get('price'))

    if 'user_name' not in data:
        result = {'result': False, 'msg': 'Username is required.'}
        return HttpResponse(json.dumps(result), content_type="text/json")
    user_name = data.get('user_name')

    # Bid must be higher than the last one
    if price <= item.price:
        result = {'result': False, 'msg': 'You have to make a higher bid.'}
        return HttpResponse(json.dumps(result), content_type="text/json")

    bids_qs = Bid.objects.filter(item_id=item).order_by('-bid_dt')

    # User cannot make a bid if his bid is already the highest
    if bids_qs.count() > 0:
        highest_bid = bids_qs[0]
        if user_name == highest_bid.user_name:
            result = {'result': False, 'msg': 'Your bid is already the highest.'}
            return HttpResponse(json.dumps(result), content_type="text/json")

    data['item_id'] = item
    new_bid = Bid.objects.create(**data)
    context = {"result": True, 'id': new_bid.id}
    return HttpResponse(json.dumps(context), content_type="text/json")


def item_bids_view(request, pk):
    """Read bids/set new bid for an item"""
    item = get_object_or_404(Item, pk=pk)
    if not(item):
        result = {'result': False, 'msg': 'Item is undefined.'}
        return HttpResponse(json.dumps(result), content_type="text/json")
    # Set bid
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        return set_bid(data, item)
    # Get bids list
    elif request.method == 'GET':
        return get_bids(item)
