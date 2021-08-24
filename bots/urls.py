from django.urls import path
from bots.views import index

app_name = 'bots'
urlpatterns = [
    path('', index, name='index'),
]
