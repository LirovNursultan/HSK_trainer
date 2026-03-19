from rest_framework import viewsets
from trainer.api.serializers import CardSerializer, DictionaryCardSerializer, MyDictionarySerializer
from trainer.models import Card, DictionaryCard, MyDictionary

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer

class DictionaryCardViewSet(viewsets.ModelViewSet):
    queryset = DictionaryCard.objects.all()
    serializer_class = DictionaryCardSerializer

class MyDictionaryViewSet(viewsets.ModelViewSet):
    queryset = MyDictionary.objects.all()
    serializer_class = MyDictionarySerializer