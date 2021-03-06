
from django.conf.urls import url
from django.urls import path, include  # add this
from . import views

app_name='visitors';

urlpatterns = [
   # path('contact/', views.visitor, name='visit'),
    url(r'^visit/$', views.visitor, name='visit'),

  #  url(r'^coll/$', views.visitor.as_view()),

]