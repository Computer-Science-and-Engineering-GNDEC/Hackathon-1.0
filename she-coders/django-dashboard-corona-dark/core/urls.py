# -*- encoding: utf-8 -*-


from django.contrib import admin
from django.urls import path, include  # add this
from . import views
urlpatterns = [
    path("", views.index), # Auth routes - login / register
    path("charts/", views.chart),
    #path("", include("app.urls"))             # UI Kits Html files
    path('admin/', admin.site.urls),
    path('add', views.addsale),
    path('tables/', views.table)

]
