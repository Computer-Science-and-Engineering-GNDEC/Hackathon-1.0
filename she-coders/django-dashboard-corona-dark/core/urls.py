# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from . import views
urlpatterns = [
    path("", views.fetch_data), # Auth routes - login / register
    #path("", include("app.urls"))             # UI Kits Html files
]
