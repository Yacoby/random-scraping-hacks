from django.db import models

class Site(models.Model):
    name = models.CharField(max_length=256)
    scrape = models.BooleanField(default=False)

    class Meta:
        db_table = 'sites'
