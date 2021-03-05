from . import views
from django.urls import path
from django.contrib import admin 

urlpatterns = [
    path('admin/', admin.site.urls),
    # configured the URL
    path('',views.index,name='index'),
]