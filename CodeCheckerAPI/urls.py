from django.conf.urls import url

from polls import views

urlpatterns = [
    url(r'^submit/', views.index, name='index')
]
