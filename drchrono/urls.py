from django.conf.urls import include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^app/$', views.app),
    url(r'^logout/$', views.leave),
    
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
