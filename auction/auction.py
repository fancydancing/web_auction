import json

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Item, Bid
from . import utils

class AuctionItem():
    def __init__(self, item_id=None):
        self.item = None
        if item_id:
            self.item = get_object_or_404(Item, pk=item_id)
            if not self.item:
                raise Exception('Item not found.')

    def add(self, data:dict):
        """
        Create new item.

        request parameters:
        [title:str] - item title
        [description:str] - item description
        [close_dt:int] - closing time for bids
        [price:int] - item start price
        """
        data['close_dt'] = utils.from_epoch(data['close_dt'])

        new_item = Item.objects.create(**data)
        return new_item.id

    def edit(self, data:dict):
        """
        Edit an item.

        parameters in data:
        [title:str] - item title
        [description:str] - item description
        [close_dt:int] - closing time for bids
        [price:str] - item start price
        """

        self.item.title = data.get('title', self.item.title)
        self.item.description = data.get('description', self.item.description)
        self.item.price = data.get('price', self.item.price)
        self.item.close_dt = utils.from_epoch(data.get('close_dt', self.item.close_dt))
        self.item.save()

        return True


    def delete(self):
        """Delete an item"""
        self.item.delete()
        return True


    def read(self):
        """Read an item"""
        result = {
            'id': self.item.id,
            'title': self.item.title,
            'description': self.item.description,
            'create_dt': utils.to_epoch(self.item.create_dt),
            'close_dt': utils.to_epoch(self.item.close_dt),
            'price': self.item.price
        }

        return result


    def get_bids(self):
        """Get bids list for an item."""
        bids_qs = Bid.objects.filter(item_id=self.item).order_by('-bid_dt')

        bids_list = [{
            "id": bid.id,
            "bid_dt": utils.to_epoch(bid.bid_dt),
            "price": bid.price,
            "user_name": bid.user_name
        } for bid in bids_qs]

        return bids_list


    def set_bid(self, data:dict):
        """
        Set a bid for an item.

        [item:Item] - instance of Item
        parameters in data:
        [price:int] - bid value
        [user_name:str] - user making a bid
        """
        price = data.get('price')
        user_name = data.get('user_name')

        if self.item.close_dt <= timezone.now():
            result = {'result': False, 'msg': 'Sorry, this lot is already closed.'}
            return result

        # Bid must be higher than the last one
        if price <= self.item.price:
            result = {'result': False, 'msg': 'You have to make a higher bid.'}
            return result

        bids_qs = Bid.objects.filter(item_id=self.item).order_by('-bid_dt')

        # User cannot make a bid if his bid is already the highest
        if bids_qs.count() > 0:
            highest_bid = bids_qs[0]
            if user_name == highest_bid.user_name:
                result = {'result': False, 'msg': 'Your bid is already the highest.'}
                return result

        data['item_id'] = self.item
        new_bid = Bid.objects.create(**data)
        result = {"result": True, 'id': new_bid.id}
        return result


class AuctionList():
    def get_list(self, data):
        """
        Return a list of items.

        request parameters:
        [page:int] - number of page
        [sort:str] - 'asc' or 'desc'
        [order:str] - field name to sort on
        [search_string:str] - string to find in title or description
        [show_closed:bool] - show closed items or not
        """
        page_number = data.get('page', 0)
        sort = data.get('sort', 'create_dt')
        order = data.get('order', 'asc')
        search_string = None # data.get('search_string', None)
        show_closed = data.get('show_closed', False)

        items_qs = Item.objects.all()
        if search_string:
            items_qs = items_qs.filter(
                Q(title__icontains=search_string) |
                Q(description__icontains=search_string)
            )

        if not show_closed:
            items_qs = items_qs.filter(close_dt__gt=timezone.now())

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
                "price": int(item.price),
            } for item in items_qs],
            'total_count': total_count
        }

        return items_list


class Authorization():
    def login(self, data):
        # Users allowed to login
        login_pass = {'admin': 'admin',
                      'user': 'user',
                      'user2': 'user2'}

        username = data.get('login')
        password = data.get('password')

        # Login/password check
        if username not in login_pass.keys() or password != login_pass[username]:
            res = False
            role = None
        else:
            res = True
            role = 'admin' if username == 'admin' else 'user'

        return {'result': res, 'login': username, 'role': role}
