from django.db import models
from django.contrib.auth.models import User
from django import forms

CITY_CHOICES = (
    ('ludhiana','LUDHIANA'),
    ('chandigarh', 'CHANDIGARH'),
)

ITEM_CHOICES = (
    ('school bag','SCHOOL BAG'),
    ('hand bag', 'HAND BAG'),
    ('travelling bag','TRAVELLING BAG'),
)

class city(models.Model) :
    id=models.AutoField(primary_key=True,blank=True,null=False)

    
    city = models.CharField( 
        max_length = 20, 

        choices = CITY_CHOICES, 
        default = 'ludhiana'
        ) 
        
  
    def __str__(self):
        return  self.city




class item(models.Model) :
    item = models.CharField( 
        max_length = 20, 

        choices = ITEM_CHOICES, 
        default = 'schoolbag'
        ) 
    stock = models.CharField(max_length=7,default="10000")
    def __str__(self):
        return  self.item

class customer(models.Model):
    id=models.AutoField(primary_key=True,blank=True,null=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.PositiveIntegerField(default=0)
    city = models.ForeignKey(city, on_delete=models.CASCADE,blank=True,null=False,default='')
    item = models.ForeignKey(item, on_delete=models.CASCADE,blank=True,null=False,default='')

    
    timestamp = models.DateTimeField(auto_now_add= True)
    quantity = models.PositiveIntegerField(default=0)
    price= models.DecimalField(max_digits=10, decimal_places=2)
    description=models.TextField(blank=True,null=False)
    def __str__(self):
        return  self.first_name

class person(models.Model):
    timestamp = models.DateTimeField(auto_now_add= True)
    in_persons = models.PositiveIntegerField(default=0)
    out_persons = models.PositiveIntegerField(default=0)
    total_persons = models.PositiveIntegerField(default=0)







