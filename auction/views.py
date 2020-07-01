from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import Item

def index(request):
    return HttpResponse("Hello, world. You're at the auction index.")

def show_html(request):
    return render(request, 'base.html')

def items_list(request):
    qs = Item.objects.order_by('-create_dt')

    items_list = [{
                   "id": item.id,
                   "title": item.title,
                   "description": item.description,
                   "create_dt": item.create_dt,
                   "close_dt": item.close_dt,
                   "start_bid": item.start_bid,
                   "price": item.price,
                   } for item in qs]

    items_json = json.dumps(items_list, cls=DjangoJSONEncoder)

    return HttpResponse(items_json, content_type="text/json")
