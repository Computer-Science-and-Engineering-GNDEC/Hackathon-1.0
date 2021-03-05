from django.db import models
from django.contrib.auth.models import User
from django import forms

CITY_CHOICES = (
    ('ludhiana','LUDHIANA'),
    ('chandigarh', 'CHANDIGARH'),
)

ITEM_CHOICES = (
    ('schoolbag','SCHOOLBAG'),
    ('handbag', 'HANDBAG'),
    ('travellingbag','TRAVELLINGBAG'),
)


class customer(models.Model):
    id=models.AutoField(primary_key=True,blank=True,null=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.PositiveIntegerField(default=0)
    city= forms.CharField(label='City', widget=forms.Select(choices=CITY_CHOICES))
    timestamp = models.DateTimeField(auto_now_add= True)
    quantity = models.PositiveIntegerField(default=0)
    price= models.DecimalField(max_digits=10, decimal_places=2)
    description=models.TextField(blank=True,null=False)
    def __str__(self):
        return "%s" % (self.city)

class location(models.Model) :
    item= forms.CharField(label='Item', widget=forms.Select(choices=ITEM_CHOICES))
    stock = models.CharField(max_length=7,default="10000")
    city = models.ForeignKey(customer, on_delete=models.CASCADE,blank=True,null=False,default='')



