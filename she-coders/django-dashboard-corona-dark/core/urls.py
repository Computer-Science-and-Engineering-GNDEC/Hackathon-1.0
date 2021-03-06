# -*- encoding: utf-8 -*-


from django.contrib import admin
from django.urls import path, include  # add this
from . import views
from django.conf.urls import url

urlpatterns = [
    path("", views.index), # Auth routes - login / register
    path("charts/", views.chart),
   # path("visitors/", include("visitors.urls")),             # UI Kits Html files
    url(r'^visitor/', include('visitors.urls')),

    path('admin/', admin.site.urls),

    path('add', views.addsale),
    path('tables/', views.table),
    

]
