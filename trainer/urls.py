from django.urls import path
from .views import create_card, card_list, edit_card, MyDictionaryListView, MyDictCardDetailView


urlpatterns = [
    path('', card_list, name='card_list'),
    path('create/', create_card, name='create_card'),
    # path('edit/', create_card, name='edit_card'),
    path('<int:pk>/edit', edit_card, name='edit_card'),

    path('my', MyDictionaryListView.as_view(), name="my_cards"),
    path('my/<int:card_id>', MyDictCardDetailView.as_view(), name="my_card")
]