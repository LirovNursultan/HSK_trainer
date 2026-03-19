from trainer.models import Card, DictionaryCard, MyDictionary
from rest_framework import serializers

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'  


class DictionaryCardSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)

    class Meta:
        model = DictionaryCard
        fields = ['id', 
            'card', 
            'added_at',       
            'is_learned',
            'times_viewed',
            'times_correct',
            'times_incorrect',          
            'last_viewed',
            'notes',]

class MyDictionarySerializer(serializers.ModelSerializer):
    dictionary_cards = DictionaryCardSerializer(many=True, read_only=True)

    class Meta:
        model = MyDictionary
        fields = '__all__'  