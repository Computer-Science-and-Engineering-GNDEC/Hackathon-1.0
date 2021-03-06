from django.contrib import admin

# Register your models here.
from .models import customer, item,city
admin.site.register(city)

admin.site.register(item)

admin.site.register(customer)



