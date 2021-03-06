# -*- encoding: utf-8 -*-
from django.urls import path, re_path, include
from app import views
from django.contrib import admin

urlpatterns = [

    # The home page

    #path('', include('core.urls')),
    # Matches any html file
    path('home', views.index, name="home"),
    #re_path(r'^.*\.*', views.pages, name='pages'),

]
