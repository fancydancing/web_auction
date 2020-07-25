import json
import operator

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404


from .models import Item, Bid, AuctionUser, AutoBid
from . import utils
from .consumers import ws_send


# Used to show all items without pagination
ALL_ITEMS = -1

# Users allowed to login
LOGIN_PASS = {
    'admin': {'password': 'admin', 'role': 'admin', 'email': 'webauctiontesting+admin@gmail.com'},
    'user': {'password': 'user', 'role': 'user', 'email': 'webauctiontesting+user@gmail.com'},
    'user2': {'password': 'user2', 'role': 'user', 'email': 'webauctiontesting+user2@gmail.com'}
    }


class AuctionItem():
    def __init__(self, item_id=None):
        self.item = None
        if item_id is not None:
            self.item = get_object_or_404(Item, pk=item_id)

    def add(self, data: dict) -> int:
        """
        Create new item.

        parameters in data:
            title: str - item title
            description: str - item description
            close_dt: int - closing time for bids
            price: int - item start price
        """

        data['close_dt'] = utils.from_epoch(data['close_dt'])
        new_item = Item.objects.create(**data)
        return new_item.id

    def edit(self, data: dict) -> bool:
        """
        Edit an item.

        parameters in data:
            title: str - item title
            description: str - item description
            close_dt: int - closing time for bids
            price: str - item start price
        """

        self.item.title = data.get('title', self.item.title)
        self.item.description = data.get('description', self.item.description)
        self.item.price = data.get('price', self.item.price)
        self.item.close_dt = utils.from_epoch(data.get('close_dt')) or self.item.close_dt
        self.item.save()

        ws_send({
            'event': 'item_changed',
            'item_id': self.item.id
        })


        return True

    def delete(self) -> bool:
        """Delete an item."""
        self.item.delete()
        return True

    def read(self) -> dict:
        """Read an item."""
        return {
            'id': self.item.id,
            'title': self.item.title,
            'description': self.item.description,
            'create_dt': utils.to_epoch(self.item.create_dt),
            'close_dt': utils.to_epoch(self.item.close_dt),
            'price': self.item.price,
            'expired': self.item.expired,
            'awarded_user': self.item.awarded_user
        }

    def get_bids(self) -> list:
        """Get bids list for an item."""
        bids_qs = Bid.objects.filter(item_id=self.item).order_by('-bid_dt')

        bids_list = []
        for bid in bids_qs:
            bids_list.append({
                'id': bid.id,
                'bid_dt': utils.to_epoch(bid.bid_dt),
                'price': bid.price,
                'user_name': bid.user_name
            })

        return bids_list

    def set_bid(self, data: dict) -> dict:
        """
        Set a bid for an item.

        item: Item - instance of Item
        parameters in data:
            price: int - bid value
            user_name: str - user making a bid
            auto: bool - autobid
        """

        price = data.get('price')
        user_name = data.get('user_name')
        auto = data.get('auto')

        if self.item.close_dt <= timezone.now():
            result = {'result': False, 'msg': 'Sorry, this lot is already closed.'}
            return result

        # Bid must be higher than the last one
        if price <= self.item.price:
            result = {'result': False, 'msg': 'You have to make a higher bid.'}
            return result

        bids_qs = Bid.objects.filter(item_id=self.item).order_by('-bid_dt')

        if bids_qs.count() > 0:
            highest_bid = bids_qs[0]
            # User cannot make a bid if his bid is already the highest
            if user_name == highest_bid.user_name:
                result = {'result': False, 'msg': 'Your bid is already the highest.'}
                return result
            # Return previous bid sum to user's autobid total amount
            # if it was made by autobid
            else:
                pass


        data['item_id'] = self.item
        new_bid = Bid.objects.create(**data)

        ws_send({
            'item_id': self.item.id,
            'event': 'new_bid'
        })

        return {'result': True, 'id': new_bid.id}

    def notify_winner(self, user_id):
        ws_send({
            'event': 'item_won',
            'item_title': self.item.title,
            'user_id': user_id,
            'price': self.item.price
        })



class AuctionList():
    def __init__(self, data: dict):
        """
        Constructor for AuctionList object.
        Parameters in data:
            page: int - number of page
            page_size: int - size of page
            sort: str - 'asc' or 'desc'
            order: str - field name to sort on
            search_string: str - string to find in title or description
            show_closed: bool - show closed items or not
        """
        self.page_number = data.get('page')
        self.page_size = data.get('page_size')
        self.sort = data.get('sort')
        self.order = data.get('order')
        self.search_string = data.get('search_string')
        self.show_closed = data.get('show_closed')


    def get_list(self) -> list:
        """
        Return a list of items.
        """

        items_qs = Item.objects.all()
        if self.search_string is not None:
            items_qs = items_qs.filter(
                Q(title__icontains=self.search_string) |
                Q(description__icontains=self.search_string)
            )

        if not self.show_closed:
            items_qs = items_qs.filter(close_dt__gt=timezone.now())

        if self.sort is not None:
            sorting_column = ('' if self.order == 'asc' else '-') + self.sort
            items_qs = items_qs.order_by(sorting_column)

        total_count = items_qs.count()
        if self.page_size != ALL_ITEMS and self.page_number is not None:
            paginator = Paginator(items_qs, self.page_size)
            # Zero page in Django is the last for the interface
            inverted_page = paginator.num_pages - int(self.page_number) - 1
            items_qs = paginator.get_page(inverted_page).object_list

        items = []
        for item in items_qs:
            items.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'create_dt': utils.to_epoch(item.create_dt),
                'close_dt': utils.to_epoch(item.close_dt),
                'price': item.price
            })
        return {
            'items': items,
            'total_count': total_count
        }

class AuctionUserInfo():

    def __init__(self, user_id=None):
        self.user = None
        if user_id is not None:
            self.user = get_object_or_404(AuctionUser, pk=user_id)


    def get_bids_list(self, data) -> list:
        """
        Return a list of current bids of a user.
        """
        user_name = data.get('user')
        status = data.get('status')
        sort = data.get('sort')

        bids_qs = Bid.objects.filter(user_name=user_name).order_by('item_id', '-bid_dt').distinct('item_id')
        bids_ids = bids_qs.values_list('id', flat=True)

        if sort == 'close_dt':
            bids_qs = Bid.objects.filter(id__in=bids_ids).order_by('item_id__close_dt')
        elif sort == 'bid_dt':
            bids_qs = Bid.objects.filter(id__in=bids_ids).order_by('-bid_dt')

        if status == 'won':
            bids_qs = bids_qs.filter(item_id__awarded_user=user_name)
        result = []

        for bid in bids_qs:
            status = ''

            if bid.item_id.awarded_user == user_name:
                status = 'won'
            elif bid.item_id.awarded_user == '':
                status = 'in_progress'
            else:
                status = 'lost'

            result.append({
                'item_id': bid.item_id.id,
                'item': bid.item_id.title,
                'dt': utils.to_epoch(bid.bid_dt),
                'close_dt': utils.to_epoch(bid.item_id.close_dt),
                'status': status,
                'user_price': bid.price,
                'max_price': bid.item_id.price
            })
        return result


    def read(self) -> dict:
        """Read user info."""
        return {
            'id': self.user.id,
            'name': self.user.name,
            'email': self.user.email,
            'autobid_total_sum': self.user.autobid_total_sum,
            'autobid_alert_perc': self.user.autobid_alert_perc
        }


    def edit(self, data: dict) -> bool:
        """
        Edit user info.

        parameters in data:
            email: str - new email
            autobid_total_sum: int - new autobid_total_sum
            autobid_alert_perc: int - new autobid_alert_perc
        """

        self.user.email = data.get('email', self.user.email)
        self.user.autobid_total_sum = data.get('autobid_total_sum', self.user.autobid_total_sum)
        self.user.autobid_alert_perc = data.get('autobid_alert_perc', self.user.autobid_alert_perc)
        self.user.save()

        return True


class AuctionAutoBid():    
    def add(self, data: dict) -> int:
        """
        Set autobid on for a user-item pair.

        parameters in data:
            user: str - user name
            item: int - item id
        """
        user = get_object_or_404(AuctionUser, name=data.get('user'))
        item = get_object_or_404(Item, pk=data.get('item'))

        data_add = {'user': user, 'item': item}
        new_autobid = AutoBid.objects.create(**data_add)

        return True

    def get_list(self, item_id: int):
        users = AutoBid.objects.filter(item__id=item_id).distinct('user').order_by('user__id')
        return users.values_list('user__id', flat=True)

    def delete(self, data: dict):
        user = data['user']
        item = data['item']

        AutoBid.objects.filter(user__name=user, item__id=item).delete()
        return True


class Authorization():
    def login(self, data: dict) -> dict:
        username = data.get('login')
        password = data.get('password')

        # Login/password check
        users = AuctionUser.objects.all()
        allowed_logins = users.values_list('name', flat=True)
        if username not in allowed_logins or password != users.get(name=username).password:
            res = False
            role = None
            username = None
        else:
            res = True
            logged_user = users.get(name=username)
            role = logged_user.role
            id = logged_user.id

        return {'result': res, 'login': username, 'role': role, 'id': id}


def check_deadlines():
    expired_items = Item.objects.filter(expired=False, close_dt__lte=timezone.now())

    awards = []
    for item in expired_items:
        bids = Bid.objects.filter(item_id=item)
        if len(bids) > 0:
            latest_bid = bids.latest('bid_dt')
            user = User.objects.get(name=latest_bid.user_name)
            awards.append({'item': item.title,
                           'item_id': item.id,
                           'price': latest_bid.price,
                           'user_name': user.name,
                           'user_id': user.id,
                           'email': user.email
                           })
        else:
            user_name = None

        item.awarded_user = user_name
        item.expired = True
        item.save()

    return awards

def check_autobidding(item_id: int, price: int):
    """
    Automatically set bid on an item for users with autobid set to True.
    """
    users_for_bidding = AuctionAutoBid().get_list(item_id)
    users_autobid_amounts = User.objects.filter()

    winner = None
    pre_max_bidder = None
    new_price = price + 1

    if len(users_for_bidding) > 0:
        winner = users_for_bidding[0]
    if len(users_for_bidding) > 1:
        pre_max_bidder = users_for_bidding[1]
        new_price = pre_max_bidder.autobid_total_sum + 1

    item = AuctionItem(item_id)
    data = {'user': winner.name, 'price': new_price, 'auto': True}
    item.set_bid(data)
    