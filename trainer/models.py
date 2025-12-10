from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    hieroglyph = models.CharField(max_length=255)
    translate = models.CharField(max_length=255)
    transcription = models.CharField(max_length=255)
    audio = models.FileField(upload_to='audio/', blank=True, null=True)

    def __str__(self):
        return f"{self.hieroglyph} - {self.translate}"
    

class MyDictionary(models.Model):
    """
    Модель для хранения карточек в личном словаре пользователя
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='dictionary',
        verbose_name='Пользователь'
    )
    
    cards = models.ManyToManyField(
        'Card',  
        through='DictionaryCard',
        related_name='in_dictionaries',
        verbose_name='Карточки'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Последнее обновление'
    )
    
    class Meta:
        verbose_name = 'Мой словарь'
        verbose_name_plural = 'Мои словари'
    
    def __str__(self):
        return f"Словарь {self.user.username}"
    

class DictionaryCard(models.Model):
    """
    Промежуточная модель для хранения дополнительной информации о карточке в словаре
    """
    dictionary = models.ForeignKey(
        MyDictionary,
        on_delete=models.CASCADE,
        related_name='dictionary_cards',
        verbose_name='Словарь'
    )
    
    card = models.ForeignKey(
        'Card',  # Замените на название вашего приложения если нужно: 'app_name.Card'
        on_delete=models.CASCADE,
        related_name='dictionary_entries',
        verbose_name='Карточка'
    )
    
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    
    # Прогресс обучения
    is_learned = models.BooleanField(
        default=False,
        verbose_name='Изучена'
    )
    
    times_viewed = models.IntegerField(
        default=0,
        verbose_name='Количество просмотров'
    )
    
    times_correct = models.IntegerField(
        default=0,
        verbose_name='Правильных ответов'
    )
    
    times_incorrect = models.IntegerField(
        default=0,
        verbose_name='Неправильных ответов'
    )
    
    last_viewed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Последний просмотр'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Личные заметки'
    )
    
    class Meta:
        unique_together = ('dictionary', 'card')
        ordering = ['-added_at']
        verbose_name = 'Карточка в словаре'
        verbose_name_plural = 'Карточки в словаре'
        indexes = [
            models.Index(fields=['dictionary', 'is_learned']),
            models.Index(fields=['dictionary', 'added_at']),
        ]
    
    def __str__(self):
        return f"{self.card.hieroglyph} в словаре {self.dictionary.user.username}"
    


# Сигналы для автоматического создания словаря при регистрации
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_dictionary(sender, instance, created, **kwargs):
    """Автоматически создать словарь при создании пользователя"""
    if created:
        MyDictionary.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_dictionary(sender, instance, **kwargs):
    """Сохранить словарь пользователя"""
    if hasattr(instance, 'dictionary'):
        instance.dictionary.save()