import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from .auction import AuctionItem, Authorization, AuctionList
from .models import Item


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
        data = json.loads(request.body.decode('utf-8'))
        params = ['title', 'description', 'close_dt', 'price']
        missing_params = [p for p in params if p not in data]
        if len(missing_params) > 0:
            result = {'result': False, 'msg': 'Missing parameters: ' + ', '.join(missing_params)}
            return HttpResponse(json.dumps(result), content_type="text/json")

        if data['price'] <= 0:
            result = {'result': False, 'msg': 'Price must be greater than 0.'}
            return HttpResponse(json.dumps(result), content_type="text/json")
        new_id = AuctionItem().add(data)
        result = {'result': True, 'id': new_id}
        return HttpResponse(json.dumps(result), content_type="text/json")
    else:
        items_list = AuctionList().get_list(request.GET)
        items_json = json.dumps(items_list, cls=DjangoJSONEncoder)
        return HttpResponse(items_json, content_type="text/json")


def item_info_view(request, pk):
    """
    Operations with an existing item depending on HTTP method.

    PUT: update item
    DELETE: delete item
    GET: read item
    """
    # Edit item
    if request.method == 'PUT':
        data = json.loads(request.body.decode('utf-8'))
        if 'price' in data and data['price'] <= 0:
            result = {'result': False, 'msg': 'Price must be greater than 0.'}
            return HttpResponse(json.dumps(result), content_type="text/json")
        result = AuctionItem(pk).edit(data)
        return HttpResponse(json.dumps({"result": result}), content_type="text/json")
    # Delete item
    elif request.method == 'DELETE':
        result = AuctionItem(pk).delete()
        return HttpResponse(json.dumps({"result": result}), content_type="text/json")
    # Read item
    elif request.method == 'GET':
        result = AuctionItem(pk).read()
        return HttpResponse(
            json.dumps(result, cls=DjangoJSONEncoder),
            content_type="text/json"
        )


def sign_in_view(request):
    """Authorize user and return role and username.

    request parameters:
    [login]
    [password]
    """
    data = json.loads(request.body.decode('utf-8'))
    result = Authorization().login(data)
    return HttpResponse(json.dumps(result), content_type="text/json")


def item_bids_view(request, pk: int):
    """Read bids/set new bid for an item"""
    # Set bid
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # Validate parameters
        if 'price' not in data:
            result = {'result': False, 'msg': 'Price is required.'}
            return HttpResponse(json.dumps(result), content_type="text/json")

        if 'user_name' not in data:
            result = {'result': False, 'msg': 'Username is required.'}
            return HttpResponse(json.dumps(result), content_type="text/json")

        result = AuctionItem(pk).set_bid(data)
        return HttpResponse(json.dumps(result), content_type="text/json")
    # Get bids list
    elif request.method == 'GET':
        bids_list = AuctionItem(pk).get_bids()
        bids_json = json.dumps(bids_list, cls=DjangoJSONEncoder)
        return HttpResponse(bids_json, content_type="text/json")

