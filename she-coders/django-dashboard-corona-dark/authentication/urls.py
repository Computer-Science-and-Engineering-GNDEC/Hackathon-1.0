# -*- encoding: utf-8 -*-


from django.urls import path
from .views import login_view, register_user
from django.contrib.auth.views import LogoutView
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    url(r'^admin/', admin.site.urls),

]
