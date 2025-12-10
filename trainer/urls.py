from django.urls import path
from .views import create_card, card_list


urlpatterns = [
    path('', card_list, name='card_list'),
    path('Create/', create_card, name='create_card'),
]