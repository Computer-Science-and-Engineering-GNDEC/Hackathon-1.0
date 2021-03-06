from django.contrib import admin

# Register your models here.
from .models import customer, item,city,person

admin.site.register(city)

admin.site.register(item)

admin.site.register(customer)

admin.site.register(person)




