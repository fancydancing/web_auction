from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from .utils import celery_send_email_task

class AuctionUser(models.Model):
    """User model"""
    name = models.TextField(null=False)
    password = models.TextField(null=False)
    role = models.TextField(null=False, default='user')
    email = models.TextField(null=False)
    autobid_total_sum = models.IntegerField(null=True)
    autobid_sum_left = models.IntegerField(null=True)
    autobid_alert_perc = models.IntegerField(null=True, default=95)


class Item(models.Model):
    """Item model."""
    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    title = models.TextField()
    create_dt = models.DateTimeField(
        null=False, default=timezone.now, verbose_name='Created at'
        )
    close_dt = models.DateTimeField(
        null=False, verbose_name='Closing at'
        )
    price = models.IntegerField(
        default=0, verbose_name='Price, $'
        )
    description = models.TextField(null=True, verbose_name='Description')
    expired = models.BooleanField(null=False, default=False)
    awarded_user = models.TextField(null=True, default='', verbose_name='User awarded')
    awarded_user_id = models.ForeignKey(
        AuctionUser, models.CASCADE, null=True, verbose_name='User'
    )


class Bid(models.Model):
    """Bid model."""
    user = models.ForeignKey(
        AuctionUser, models.CASCADE, null=False, verbose_name='User'
    )
    user_name = models.TextField()
    bid_dt = models.DateTimeField(null=False, default=timezone.now, verbose_name='Set at')
    auto = models.BooleanField(null=False, default=False)
    item_id = models.ForeignKey(
        Item, models.CASCADE, null=False, verbose_name='Item title'
    )
    price = models.IntegerField(
        default=0, verbose_name='Bid value'
    )

def get_spent_autobid_sum(user_id: int):
        bids_qs = Bid.objects.filter(user__id=user_id, item_id__expired=False).order_by('item_id', '-bid_dt').distinct('item_id')
        autobid_spent = 0

        for bid in bids_qs:
            # Count only winning bids
            if bid.price == bid.item_id.price and bid.auto:
                autobid_spent += bid.price

        return autobid_spent

def post_save_update_item_price(sender, instance, *args, **kwargs):
    """Updating item price after new bid."""
    if instance.item_id is not None:
        item = instance.item_id
        item.price = instance.price
        item.save()

def post_save_update_autobid_sum(sender, instance, *args, **kwargs):
    """Update autobid sum left for user after new autobid."""
    if instance.auto and instance.user is not None:
        user = instance.user
        sum_left = user.autobid_total_sum - get_spent_autobid_sum(user.id)
        user.autobid_sum_left = sum_left
        user.save()

        if sum_left == 0:
            email_subject = 'Webauction alert: you are run out of autobid sum'
            email_content = 'Your total autobid amount is 0. The last item to bid was ' + instance.item_id.title + ' with a price of ' + str(instance.price) + '. Come to webauction.herokuapp.com for more opportunities!'
            email_recipients = [user.email]
            celery_send_email_task(email_subject, email_content, email_recipients)

post_save.connect(post_save_update_item_price, sender=Bid)
post_save.connect(post_save_update_autobid_sum, sender=Bid)


class AutoBid(models.Model):
    item = models.ForeignKey(
        Item, models.CASCADE, null=False, verbose_name='Item'
    )
    user = models.ForeignKey(
        AuctionUser, models.CASCADE, null=False, verbose_name='User'
    )
    create_dt = models.DateTimeField(null=False, default=timezone.now, verbose_name='Set at')

class DeployInfo(models.Model):
    """Info about deployed DB data."""
    deploy_name = models.TextField(null=True)
