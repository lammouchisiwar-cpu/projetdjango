from django.urls import path

from .views import *
app_name="Expedition"
urlpatterns=[
    path('home/',home,name="home"),
    path('w/<str:name>', welcome, name="welcomeFunction"),
    path('list/',listExpedition, name="list"),
    path('details/<int:id>/',detailExpedition, name="detail")
]