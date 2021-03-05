from django.contrib import admin

# Register your models here.
from .models import customer, location

admin.site.register(customer)
admin.site.register(location)



