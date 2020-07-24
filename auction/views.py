import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404

from .auction import AuctionItem, Authorization, AuctionList, AuctionUserInfo, AuctionAutoBid
from .models import Item, AuctionUser
from .forms import ItemListForm, ItemForm
from .deploy_db import deploy_data


def add_item(request) -> HttpResponse:
    """
    Add new item.

    Parameters in request:
        title: str - item title
        description: str - item description
        close_dt: int - closing time for item
        price: int - item price
    """
    data = json.loads(request.body.decode('utf-8'))
    item_form = ItemForm(data)
    if item_form.is_valid():
        new_id = AuctionItem().add(item_form.cleaned_data)
        result = {'result': True, 'id': new_id}
    else:
        result = {'result': False, 'msg': item_form.errors.as_data()}

    return HttpResponse(json.dumps(result), content_type='text/json')


def get_items_list(request) -> HttpResponse:
    """
    Get a list of items.

    Parameters in request:
        page: int - number of page
        page_size: int - size of page
        sort: str - 'asc' or 'desc'
        order: str - field name to sort on
        search_string: str - string to find in title or description
        show_closed: bool - show closed items or not
    """
    items_form = ItemListForm(request.GET)
    if items_form.is_valid():
        items_list = AuctionList(items_form.cleaned_data).get_list()
        result = json.dumps(items_list)
    else:
        result = {'items': []}
    return HttpResponse(result, content_type='text/json')


def items_view(request) -> HttpResponse:
    """
    Operations with items depending on HTTP method.

    POST: add new item
    GET: return a list of all items
    """
    if request.method == 'POST':
        return add_item(request)
    else:
        return get_items_list(request)

def update_item(request, pk: int) -> HttpResponse:
    """
    Update an item.

    Parameters in request (all optional):
        title: str - new item title
        description: str - new item description
        price: int - new item price
        close_dt: int - new closing time
    """
    data = json.loads(request.body.decode('utf-8'))
    item_form = ItemForm(data)
    if item_form.is_valid():
        result = AuctionItem(pk).edit(data)
        res = {'result': result}
    else:
        res = {'result': False, 'msg': item_form.errors.as_data()}

    return HttpResponse(json.dumps(res), content_type='text/json')


def delete_item(pk: int) -> HttpResponse:
    """
    Delete an item.

    pk: int - item ID
    """
    result = AuctionItem(pk).delete()
    return HttpResponse(json.dumps({'result': result}), content_type='text/json')


def read_item(pk: int) -> HttpResponse:
    """
    Read an item.

    pk: int - item ID
    """
    result = AuctionItem(pk).read()
    return HttpResponse(json.dumps(result),content_type='text/json')


def item_info_view(request, pk) -> HttpResponse:
    """
    Operations with an existing item depending on HTTP method.

    PUT: update item
    DELETE: delete item
    GET: read item
    """
    # Edit item
    if request.method == 'PUT':
        return update_item(request, pk)
    # Delete item
    elif request.method == 'DELETE':
        return delete_item(pk)
    # Read item
    elif request.method == 'GET':
        return read_item(pk)


def sign_in_view(request) -> HttpResponse:
    """
    Authorize user and return role and username.

    Parameters in request:
        login: str - user login
        password: str - user password
    """
    data = json.loads(request.body.decode('utf-8'))
    result = Authorization().login(data)
    return HttpResponse(json.dumps(result), content_type='text/json')


def set_bid(request, pk: int) -> HttpResponse:
    """
    Set new bid.

    Parameters in request:
        price: int - bid sum
        user_name: str - user login
    """
    data = json.loads(request.body.decode('utf-8'))
    # Validate parameters
    if 'price' not in data:
        result = {'result': False, 'msg': 'Price is required.'}
    elif 'user_name' not in data:
        result = {'result': False, 'msg': 'Username is required.'}
    else:
        result = AuctionItem(pk).set_bid(data)
    return HttpResponse(json.dumps(result), content_type='text/json')


def bids_list(pk: int) -> HttpResponse:
    """
    Get a list of all bids for an item.

    pk: int - item ID
    """
    bids_list = AuctionItem(pk).get_bids()
    return HttpResponse(json.dumps(bids_list), content_type='text/json')


def item_bids_view(request, pk: int) -> HttpResponse:
    """Read bids/set new bid for an item."""
    # Set bid
    if request.method == 'POST':
        return set_bid(request, pk)
    # Get bids list
    elif request.method == 'GET':
        return bids_list(pk)

def item_set_autobid(request, item_id: int):
    """
    Set or unset autobid on an item for a particular user
    
    item_id: int - item for autobid

    Parameters in request:
        user_name: str - user name
        auto_bid: bool - turn autobid on/off
    """
    data = {'user': request.get('user_name'),
            'item': item_id
        }
    
    if request.get('auto_bid'):
        AuctionAutoBid().add(data)
    else:
        AuctionAutoBid().delete(data)
    

def user_bids(request, userid: int):
    """Get user's current bids"""
    bids_list = AuctionUserInfo(request).get_bids_list()
    return HttpResponse(json.dumps(bids_list), content_type='text/json')


def read_user(pk: int) -> HttpResponse:
    """
    Read user info.

    pk: int - user ID
    """
    result = AuctionUserInfo(pk).read()
    return HttpResponse(json.dumps(result),content_type='text/json')


def update_user(request, pk: int) -> HttpResponse:
    """
    Update user.

    Parameters in request (all optional):
        email: str - new email
        autobid_total_sum: int - new autobid_total_sum
        autobid_alert_perc: int - new autobid_alert_perc
    """
    data = json.loads(request.body.decode('utf-8'))
    # item_form = ItemForm(data)
    # if item_form.is_valid():
    result = AuctionUserInfo(pk).edit(data)
    res = {'result': result}
    return HttpResponse(json.dumps(res), content_type='text/json')



def user_info_view(request, pk) -> HttpResponse:
    """
    Operations with current user depending on HTTP method.

    PUT: update user info
    GET: read user info
    """
    # Edit user info
    if request.method == 'PUT':
        return update_user(request)
    # Read user info
    elif request.method == 'GET':
        return read_user(pk)
        


def index_view(request) -> HttpResponse:
    """Show start page with items list."""
    deploy_data()
    return render(request, 'items.html')