from django.db import models
from django.utils import timezone

# Items
class Item(models.Model):
    def __unicode__(self):
        return self.title

    def __str__(self):
         return self.title

    title = models.CharField(max_length=255)
    create_dt = models.DateTimeField(null=False, default=timezone.now, verbose_name='Created at')
    close_dt = models.DateTimeField(null=False, verbose_name='Closing at')
    price = models.DecimalField(default=0, decimal_places=0, max_digits=20, verbose_name='Price, $')
    description = models.CharField(max_length=255, null=True)

# Bids
class Bid(models.Model):
    user_name = models.CharField(max_length=255)
    bid_dt = models.DateTimeField(null=False, default=timezone.now)
    item_id = models.ForeignKey(Item, models.CASCADE, null=False, verbose_name='Item title')
    price = models.DecimalField(default=0, decimal_places=0, max_digits=20, verbose_name='Sum, $')
