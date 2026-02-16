from django.urls import path
from .views import create_card, card_list, edit_card, add_to_dictionary, MyDictionaryListView, MyDictCardDetailView,  MyDictionaryPDFView, toggle_learned, remove_from_dictionary
from . import views

urlpatterns = [
    path('', card_list, name='card_list'),
    path('create/', create_card, name='create_card'),
    # path('edit/', create_card, name='edit_card'),
    path('<int:pk>/edit', edit_card, name='edit_card'),
    
    path('my', MyDictionaryListView.as_view(), name="my_cards"),
    path('my/<int:card_id>/', MyDictCardDetailView.as_view(), name="my_card_detail"),
    path('my/pdf/', MyDictionaryPDFView.as_view(), name='my_cards_pdf'),

    path('api/dictionary/add/', add_to_dictionary, name='add_to_dictionary'),
    path('api/dictionary/toggle-learned/', toggle_learned, name='toggle_learned'),
    path('api/dictionary/remove/', remove_from_dictionary, name='remove_from_dictionary'),
    path('train/', views.trainers_home, name='trainers_home'),
    path('train/flashcards/', views.flashcards_session, name='flashcards_session'),
]