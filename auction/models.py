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
    start_bid = models.DecimalField(default=0.00, decimal_places=2, max_digits=20, verbose_name='Start bid, $')
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=20, verbose_name='Price, $')
    description = models.CharField(max_length=255, null=True)
