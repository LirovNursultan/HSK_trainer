from rest_framework import serializers
from trainer.models import Card, DictionaryCard, MyDictionary


# КАРТОЧКИ 
class SimpleCardSerializer(serializers.ModelSerializer):
    """Лёгкая версия для списков, тренировок и вложенных объектов"""
    class Meta:
        model = Card
        fields = ['id', 'hieroglyph', 'transcription', 'translate', 'audio']


class CardSerializer(serializers.ModelSerializer):
    """Полная версия (для админки админке)"""
    class Meta:
        model = Card
        fields = '__all__'


# ЛИЧНЫЙ СЛОВАРЬ 
class DictionaryCardSerializer(serializers.ModelSerializer):
    """Основной сериализатор для записей в словаре пользователя"""
    card = SimpleCardSerializer(read_only=True)
    accuracy = serializers.SerializerMethodField()

    class Meta:
        model = DictionaryCard
        fields = [
            'id',
            'card',
            'added_at',
            'is_learned',
            'times_viewed',
            'times_correct',
            'times_incorrect',
            'accuracy',
            'last_viewed',
            'notes',
        ]
        read_only_fields = ['added_at', 'last_viewed', 'accuracy']

    def get_accuracy(self, obj):
        return obj.get_accuracy()


# СТАТИСТИКА СЛОВАРЯ 
class MyDictionarySerializer(serializers.ModelSerializer):
    """Сериализатор самого словаря (для статистики)"""
    username = serializers.CharField(source='user.username', read_only=True)
    total_cards = serializers.IntegerField(source='get_cards_count', read_only=True)

    class Meta:
        model = MyDictionary
        fields = ['id', 'username', 'created_at', 'updated_at', 'total_cards']

class AddToDictionarySerializer(serializers.Serializer):
    card_id = serializers.IntegerField()

    def validate_card_id(self, value):
            if not Card.objects.filter(id=value).exists():
                raise serializers.ValidationError("Карточка с таким ID не найдена.")
            return value
    
    
class ProgressSerializer(serializers.Serializer):
    total_cards = serializers.IntegerField()
    learned_cards = serializers.IntegerField()
    accuracy_avg = serializers.FloatField()
    streak_days = serializers.IntegerField(default=0)  
    last_study_date = serializers.DateTimeField(allow_null=True)