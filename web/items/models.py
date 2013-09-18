from django.db import models
from sources.models import Site

class Item(models.Model):
    name = models.CharField(max_length=256)
    url = models.CharField(max_length=256, unique=True)
    description = models.TextField(null=True)
    rrp = models.DecimalField(null=True,max_digits=10, decimal_places=2)

    review_count = models.IntegerField(null=True)
    rating = models.FloatField(null=True)

    image_url = models.CharField(null=True,max_length=256)

    site = models.ForeignKey(Site)

    class Meta:
        db_table = 'items'

class Price(models.Model):
    item = models.ForeignKey(Item)
    date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'prices'
