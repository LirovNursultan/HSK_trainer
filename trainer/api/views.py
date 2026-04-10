from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from trainer.models import Card, DictionaryCard
from trainer.api.serializers import SimpleCardSerializer, DictionaryCardSerializer, AddToDictionarySerializer


class CardViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр общей базы HSK карточек"""
    queryset = Card.objects.all().order_by('id')
    serializer_class = SimpleCardSerializer          # используем лёгкую версию
    permission_classes = [AllowAny]           # можно поставить AllowAny, если нужно публично


class MyDictionaryViewSet(viewsets.ModelViewSet):
    """Личный словарь пользователя — только свои данные"""
    serializer_class = DictionaryCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DictionaryCard.objects.filter(
            dictionary__user=self.request.user
        ).select_related('card').order_by('-added_at')

    def perform_create(self, serializer):
        # Автоматически привязываем к словарю текущего пользователя
        dictionary = self.request.user.dictionary
        serializer.save(dictionary=dictionary)

    # Дополнительное действие — добавить карточку по card_id
    @action(detail=False, methods=['post'])
    def add(self, request):
        serializer = AddToDictionarySerializer(data=request.data)
        if serializer.is_valid():
            card_id = serializer.validated_data['card_id']
            card = Card.objects.get(id=card_id)
            dictionary = request.user.dictionary

            entry, created = DictionaryCard.objects.get_or_create(
                dictionary=dictionary,
                card=card
            )
            if created:
                return Response({"message": "Карточка добавлена в словарь"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Карточка уже в словаре"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
