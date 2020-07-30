import json
import operator

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Item, Bid, AuctionUser, AutoBid, get_spent_autobid_sum
from . import utils


# Used to show all items without pagination
ALL_ITEMS = -1

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

        utils.celery_send_ws_task({
            'event': 'item_changed',
            'item_id': self.item.id
        })


        return True

    def delete(self) -> bool:
        """Delete an item."""
        self.item.delete()
        return True

    def read(self, data=None) -> dict:
        """Read an item."""
        return {
            'id': self.item.id,
            'title': self.item.title,
            'description': self.item.description,
            'create_dt': utils.to_epoch(self.item.create_dt),
            'close_dt': utils.to_epoch(self.item.close_dt),
            'price': self.item.price,
            'expired': self.item.expired,
            'awarded_user': self.item.awarded_user,
            'awarded_user_id': self.item.awarded_user_id.id if self.item.awarded_user_id else None
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
                'user_id': bid.user.id,
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
        user = get_object_or_404(AuctionUser, name=user_name)
        auto = data.get('auto')
        notify_previous = False
        prev_winner = None

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
            # if user_name == highest_bid.user_name:
            if user == highest_bid.user:
                result = {'result': False, 'msg': 'Your bid is already the highest.'}
                return result
            else:
                # prev_winner = get_object_or_404(AuctionUser, name=highest_bid.user_name)
                prev_winner = highest_bid.user
                previous_price = self.item.price
                # Return previous bid sum to user's autobid left amount if it was made by autobid
                if highest_bid.auto:
                    AuctionUserInfo(prev_winner.id).update_auto_bid(previous_price)
                # Notify previous winner
                notify_previous = True

        data['item_id'] = self.item
        data['user'] = user
        new_bid = Bid.objects.create(**data)

        if not auto:
            # For manual bid - start checking for possible autobids
            check_autobidding()
        else:
            # For autobid - check if spent sum exceeds alert percentage
            AuctionUserInfo(user.id).check_alert_perc()

        # Send notification for list refresh
        utils.celery_send_ws_task({
            'item_id': self.item.id,
            'event': 'new_bid'
        })

        # Send notification for previous winner
        if notify_previous:
            # Notify via websocket
            utils.celery_send_ws_task({
                'event': 'item_losing',
                'user_id': prev_winner.id,
                'winner_name': user_name,
                'item_title': self.item.title,
                'item_price': price,
                'user_bid_price': previous_price
                })

            # Notify via email
            email_subject = 'Webauction alert: item outbid'
            email_content = 'There''s a higher bid on item "' + self.item.title + '": $' + str(price) + '. You current bid is $' + str(previous_price) + '. Come to webauction.herokuapp.com for more opportunities!'
            email_recipients = [prev_winner.email]
            utils.celery_send_email_task(email_subject, email_content, email_recipients)

        return {'result': True, 'id': new_bid.id}

    def notify_winner(self, user_id):
        utils.celery_send_ws_task({
            'event': 'item_won',
            'item_title': self.item.title,
            'user_id': user_id,
            'price': self.item.price
        })

    def notify_loser(self, user_id):
        utils.celery_send_ws_task({
            'event': 'item_lost',
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
            # if sort ==
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

    def check_alert_perc(self):
        sum_total = self.user.autobid_total_sum
        sum_left = self.user.autobid_sum_left
        sum_spent = (sum_total - sum_left)
        perc_used = sum_spent * 100 / sum_total

        if perc_used >= self.user.autobid_alert_perc:
            email_subject = 'Webauction autobid alert'
            email_content = 'You have already spent '+ str(self.user.autobid_alert_perc) + '% of your total autobid sum ($' + str(sum_spent) + ' of $' + str(sum_total) + '). Come to webauction.herokuapp.com for more opportunities!'
            email_recipients = [self.user.email]
            utils.celery_send_email_task(email_subject, email_content, email_recipients)
            utils.celery_send_ws_task({
                'event': 'autobid_exceeding',
                'user_id': self.user.id,
                'autobid_total_sum': sum_total,
                'autobid_spent': sum_spent
            })



    def get_bids_list(self, data) -> list:
        """
        Return a list of current bids of a user.
        """
        user_name = data.get('user')
        user = get_object_or_404(AuctionUser, name=user_name)
        status = data.get('status')
        sort = data.get('sort')

        bids_qs = Bid.objects.filter(user=user).order_by('item_id', '-bid_dt').distinct('item_id')
        bids_ids = bids_qs.values_list('id', flat=True)

        if sort == 'close_dt':
            bids_qs = Bid.objects.filter(id__in=bids_ids).order_by('-item_id__close_dt')
        elif sort == 'bid_dt':
            bids_qs = Bid.objects.filter(id__in=bids_ids).order_by('-bid_dt')

        if status == 'won':
            bids_qs = bids_qs.filter(item_id__awarded_user_id=user)
        result = []

        for bid in bids_qs:
            status = ''

            if bid.item_id.expired:
                status = 'won' if bid.item_id.awarded_user_id == user else 'lost'
            else:
                status = 'in_progress'

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
            'autobid_sum_left': self.user.autobid_sum_left,
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
        current_autobid_sum = self.user.autobid_total_sum or 0
        new_autobid_sum = int(data.get('autobid_total_sum', current_autobid_sum))

        current_autobid_alert_perc = self.user.autobid_alert_perc or 0
        new_autobid_alert_perc = min(100, int(data.get('autobid_alert_perc', self.user.autobid_alert_perc)))

        self.user.email = data.get('email', self.user.email)
        self.user.autobid_total_sum = new_autobid_sum
        self.user.autobid_sum_left = new_autobid_sum - get_spent_autobid_sum(self.user.id)
        self.user.autobid_alert_perc = new_autobid_alert_perc
        self.user.save()

        if new_autobid_sum > current_autobid_sum:
            check_autobidding()

        if new_autobid_alert_perc < current_autobid_alert_perc:
            self.check_alert_perc()

        return True

    def update_auto_bid(self, amount: int) -> int:
        """
        Update autobid left sum by an amount.
        """
        self.user.autobid_sum_left = (self.user.autobid_sum_left or 0) + amount
        self.user.save()

        return self.user.autobid_sum_left


class AuctionAutoBid():
    def add(self, data: dict) -> int:
        """
        Set autobid on for a user-item pair.

        parameters in data:
            user: str - user name
            item: int - item id
        """
        user = get_object_or_404(AuctionUser, pk=data.get('user'))
        item = get_object_or_404(Item, pk=data.get('item'))

        data_add = {'user': user, 'item': item}
        new_autobid = AutoBid.objects.create(**data_add)
        # Start a task for autobidding
        utils.celery_send_autobid_task()

        return {'result': True, 'auto_bid_state': True}

    def get_items_list(self):
        autobid_items_ids = AutoBid.objects.filter(item__expired=False).distinct('item').values_list('item', flat=True)
        autobid_items = Item.objects.filter(id__in=autobid_items_ids).order_by('close_dt')
        return autobid_items

    def get_autobid_users_list(self, item_id: int):
        # All users who have set autobid ON for this item
        autobid_users = AutoBid.objects.filter(item__id=item_id).distinct('user').order_by('user__id')
        user_ids = autobid_users.values_list('user__id', flat=True)
        users = AuctionUser.objects.filter(id__in=user_ids)
        item = get_object_or_404(Item, id=item_id)

        bids_qs = Bid.objects.filter(item_id=item).order_by('-bid_dt')
        if len(bids_qs) > 0:
            highest_bid = bids_qs[0]
            current_winner = highest_bid.user
        else:
            current_winner = None
        result = []
        for user in users:
            free_autobid_sum = user.autobid_sum_left or 0
            # Include only users who can make a higher bid
            if free_autobid_sum > item.price:
                result.append({'user_id': user.id,
                            'user_name': user.name,
                            'free_autobid_sum': free_autobid_sum,
                            'current_winner': user == current_winner
                            })
            # Others will get an email alerting about not enough sum
            else:
                email_subject = 'Webauction alert: cannot make an autobid'
                email_content = 'You have set AUTOBID option on for an item "'+ item.title + '" but there was not enough sum for the next bid. Your current balance is $' + str(free_autobid_sum) + ' and item''s price is $' + str(item.price) + '. Come to webauction.herokuapp.com for more opportunities!'
                email_recipients = [user.email]
                utils.celery_send_email_task(email_subject, email_content, email_recipients)

        # Users who can make a bid sorted by free autobid sum
        result = sorted(result, key=lambda k: k['free_autobid_sum'], reverse=True)
        return result

    def delete(self, data: dict):
        """
        Set autobid off for a user-item pair.

        parameters in data:
            user: str - user name
            item: int - item id
        """

        user = data['user']
        item = data['item']

        AutoBid.objects.filter(user__name=user, item__id=item).delete()
        return {'result': True, 'auto_bid_state': False}


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
            id = None
        else:
            res = True
            logged_user = users.get(name=username)
            role = logged_user.role
            id = logged_user.id

        return {'result': res, 'login': username, 'role': role, 'id': id}


def check_deadlines():
    expired_items = Item.objects.filter(expired=False, close_dt__lte=timezone.now())

    awards = []
    losers = []
    auto = False
    for item in expired_items:
        bids = Bid.objects.filter(item_id=item)
        if len(bids) > 0:
            latest_bid = bids.latest('bid_dt')
            auto = latest_bid.auto
            winner = latest_bid.user
            winner_name = winner.name
            awards.append({'item': item.title,
                           'item_id': item.id,
                           'price': latest_bid.price,
                           'user_name': winner_name,
                           'user_id': winner.id,
                           'email': winner.email
                           })

            losers_ids = bids.exclude(user__in=[winner]).values_list('user', flat=True).distinct()
            losers_qs = AuctionUser.objects.filter(id__in=losers_ids)
            for loser in losers_qs:
                losers.append({'item': item.title,
                               'item_id': item.id,
                               'price': latest_bid.price,
                               'winner_name': winner_name,
                               'loser_name': loser.name,
                               'loser_id': loser.id,
                               'email': loser.email
                               })
        else:
            winner_name = None
            winner = None

        item.awarded_user = winner_name
        item.awarded_user_id = winner
        item.expired = True
        item.save()

        if winner is not None and auto:
            winner.autobid_total_sum = winner.autobid_total_sum - item.price
            winner.save()

    return awards, losers

def check_autobidding():
    """
    Go through all items where at least one user has autobidding option on.
    Make all necessary bids and check items again.
    Stop when there are no new bids.
    """
    items = AuctionAutoBid().get_items_list()

    result = False
    for item in items:
        item_result = check_autobidding_for_item(item.id, item.price)
        result = result or item_result

    if result:
        check_autobidding()
    else:
        return True

def check_autobidding_for_item(item_id: int, price: int) -> bool:
    """
    Automatically set bid on an item for users with autobid set to True.
    Returns True if any bid was set, False otherwise.
    """
    users_for_bidding = AuctionAutoBid().get_autobid_users_list(item_id)

    new_price = price + 1
    set_max_price = False
    # If there are no possible bidders, quit
    if len(users_for_bidding) == 0:
        return False
    elif users_for_bidding[0].get('current_winner'):
        # If current winner is the only possible bidder, quit
        if len(users_for_bidding) == 1:
            return False
        # If current winner has max free sutobid sum, next bidder must bid maximum possible sum
        else:
            set_max_price = True
            winner = users_for_bidding[1]
            winner_sum = winner.get('free_autobid_sum')
    # If someone else has maximum autobid sum, regard him as a next winner
    else:
        winner = users_for_bidding[0]
        winner_sum = winner.get('free_autobid_sum')

    if set_max_price:
        new_price = winner_sum
    else:
        # Calculate new price: overbid the second winner by 1
        for bid_user in users_for_bidding:
            pre_max_sum = bid_user.get('free_autobid_sum')
            if pre_max_sum < winner_sum:
                new_price = pre_max_sum + 1
                break

    item = AuctionItem(item_id)
    data = {'user_name': winner.get('user_name'), 'price': new_price, 'auto': True}
    item.set_bid(data)
    return True
