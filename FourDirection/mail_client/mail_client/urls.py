"""mail_client URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from read_mail.views import home, compose, register, logout, show_mail
from django.urls import include
from read_mail.forms import LoginForm

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', home),
    url(r'^change-password/$', PasswordChangeView.as_view(success_url='/login')),
    url(r'^password-reset-complete/$', PasswordResetCompleteView.as_view(),name = 'password_reset_complete'),
    url(r'^password-reset-confirm/$', PasswordResetConfirmView.as_view(),name = 'password_reset_confirm'),
    url(r'^password-reset/done/$', PasswordResetDoneView.as_view(),name = 'password_reset_done'),
    url(r'^password-reset/$', PasswordResetView.as_view(),name = 'password_reset'),
    url(r'^login/$', LoginView.as_view(authentication_form=LoginForm)),
    url(r'^compose/$', compose),
    url(r'^register/$', register),
    url(r'^logout/$', logout),
    url(r'^mails/(?P<mail_id>\d+)/$', show_mail),
]
