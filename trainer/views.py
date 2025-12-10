from django.shortcuts import render, redirect
from .forms import CardForm
from .models import Card


def card_list(request):
    cards = Card.objects.all()
    return render(request, 'trainer/card_list.html', {'cards': cards})
    
    
def create_card(request):
    if request.method == 'POST':
        form = CardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('card_list')
    else:
        form = CardForm()
    return render(request, 'trainer/create_card.html', {'form': form})

def edit_card(request, card_id):
    card = Card.objects.get(id = card_id)
    if request.method == 'POST':
        form = CardForm(request.POST, request.files, instance= card)
        if form.is_valid():
            form.save()
            return redirect('card_list')
    else:
        form = CardForm(instance=card)
    return render (request, 'trainer/edit_card.html', {'form': form})

def delete_card(request, card_id):
    card = Card.objects.get(id=card_id)


# CBV
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F
from django.core.paginator import Paginator
from .models import Card, DictionaryCard, MyDictionary


class MyDictionaryListView(LoginRequiredMixin, ListView):
    """
    Отображение карточек из личного словаря пользователя
    """
    model = Card
    template_name = 'trainer/my_card_list.html'
    context_object_name = 'cards'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        """
        Получить только карточки из словаря текущего пользователя
        """
        user_dictionary = MyDictionary.objects.get(user=self.request.user)
        
        queryset = user_dictionary.cards.all()
        
        # Фильтрация по статусу изученности
        status_filter = self.request.GET.get('status')
        if status_filter == 'learned':
            queryset = queryset.filter(
                dictionary_entries__dictionary=user_dictionary,
                dictionary_entries__is_learned=True
            )
        elif status_filter == 'not_learned':
            queryset = queryset.filter(
                dictionary_entries__dictionary=user_dictionary,
                dictionary_entries__is_learned=False
            )
        
        # Поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(hieroglyph__icontains=search_query) |
                Q(translate__icontains=search_query) |
                Q(transcription__icontains=search_query)
            )
        
        # Сортировка
        sort_by = self.request.GET.get('sort', '-added_at')
        if sort_by == 'added_at':
            queryset = queryset.order_by(
                'dictionary_entries__added_at'
            )
        elif sort_by == '-added_at':
            queryset = queryset.order_by(
                '-dictionary_entries__added_at'
            )
        elif sort_by == 'accuracy':
            queryset = queryset.annotate(
                accuracy=F('dictionary_entries__times_correct') / 
                        (F('dictionary_entries__times_correct') + 
                         F('dictionary_entries__times_incorrect') + 1)
            ).order_by('-accuracy')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        """
        Добавить дополнительную информацию в контекст
        """
        context = super().get_context_data(**kwargs)
        
        user_dictionary = MyDictionary.objects.get(user=self.request.user)
        
        # Общая статистика
        context['total_cards'] = user_dictionary.get_cards_count()
        context['learned_cards'] = DictionaryCard.objects.filter(
            dictionary=user_dictionary,
            is_learned=True
        ).count()
        context['not_learned_cards'] = DictionaryCard.objects.filter(
            dictionary=user_dictionary,
            is_learned=False
        ).count()
        
        # Фильтры и сортировка (для отображения в шаблоне)
        context['current_status'] = self.request.GET.get('status', 'all')
        context['current_sort'] = self.request.GET.get('sort', '-added_at')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Добавить информацию о каждой карточке из словаря
        cards_with_info = []
        for card in context['cards']:
            dict_entry = DictionaryCard.objects.get(
                dictionary=user_dictionary,
                card=card
            )
            card.dict_entry = dict_entry
            card.accuracy = dict_entry.get_accuracy()
            cards_with_info.append(card)
        
        context['cards'] = cards_with_info
        
        return context


class MyDictCardDetailView(LoginRequiredMixin, DetailView):
    """
    Детальный просмотр карточки из словаря с дополнительной информацией
    """
    model = DictionaryCard
    template_name = 'trainer/my_card_detail.html'
    context_object_name = 'card_info'
    login_url = 'login'
    
    def get_object(self):
        """
        Получить запись о карточке в словаре
        """
        card_id = self.kwargs.get('card_id')
        user_dictionary = MyDictionary.objects.get(user=self.request.user)
        
        return DictionaryCard.objects.get(
            dictionary=user_dictionary,
            card_id=card_id
        )
    
    def get_context_data(self, **kwargs):
        """
        Добавить подробную информацию
        """
        context = super().get_context_data(**kwargs)
        
        dict_entry = self.get_object()
        context['card'] = dict_entry.card
        context['card_info'] = dict_entry
        context['accuracy'] = dict_entry.get_accuracy()
        
        return context