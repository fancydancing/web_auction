import json

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import Item, Bid
from . import utils

class AuctionItem():
    def add(self, data):
        """
        Create new item.

        request parameters:
        [title] - item title
        [description] - item description
        [close_dt] - closing time for bids
        [price] - item start price
        """
        data['close_dt'] = utils.from_epoch(data['close_dt'])

        new_item = Item.objects.create(**data)
        return new_item.id

    def edit(self, data, item):
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

        return True


    def delete(self, item):
        """Delete an item"""
        item.delete()
        return True


    def read(self, item):
        """Read an item"""
        result = {
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'create_dt': utils.to_epoch(item.create_dt),
            'close_dt': utils.to_epoch(item.close_dt),
            'price': item.price
        }

        return result


    def get_bids(self, item):
        """Get bids list for an item."""
        bids_qs = Bid.objects.filter(item_id=item).order_by('-bid_dt')

        bids_list = [{
            "id": bid.id,
            "bid_dt": utils.to_epoch(bid.bid_dt),
            "price": bid.price,
            "user_name": bid.user_name
        } for bid in bids_qs]

        return bids_list


    def set_bid(self, data, item):
        """
        Set a bid for an item.

        [item] - instance of Item
        parameters in data:
        [price] - bid value
        [user_name] - user making a bid
        """
        price = int(data.get('price'))
        user_name = data.get('user_name')

        if item.close_dt <= timezone.now():
            result = {'result': False, 'msg': 'Sorry, this lot is already closed.'}
            return result

        # Bid must be higher than the last one
        if price <= item.price:
            result = {'result': False, 'msg': 'You have to make a higher bid.'}
            return result

        bids_qs = Bid.objects.filter(item_id=item).order_by('-bid_dt')

        # User cannot make a bid if his bid is already the highest
        if bids_qs.count() > 0:
            highest_bid = bids_qs[0]
            if user_name == highest_bid.user_name:
                result = {'result': False, 'msg': 'Your bid is already the highest.'}
                return result

        data['item_id'] = item
        new_bid = Bid.objects.create(**data)
        result = {"result": True, 'id': new_bid.id}
        return result


class AuctionItems():
    def get_list(self, data):
        """
        Return a list of items.

        request parameters:
        [page] - number of page
        [sort] - 'asc' or 'desc'
        [order] - field name to sort on
        [search_string] - string to find in title or description
        [show_closed] - show closed items or not
        """
        page_number = data.get('page', 0)
        sort = data.get('sort', 'create_dt')
        order = data.get('order', 'asc')
        search_string = data.get('search_string', None)
        show_closed = data.get('show_closed', False)

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
