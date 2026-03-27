from django.shortcuts import render, redirect
from .forms import CardForm
from .models import Card
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from datetime import date
# Для добавления карточки в мой всловарь
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from .models import Card, MyDictionary, DictionaryCard
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
@require_POST
def mark_result(request):
    """
    Записывает результат ответа пользователя по карточке.
    Обновляет: times_correct / times_incorrect / times_viewed / last_viewed
 
    POST body: { "card_id": int, "result": "correct" | "incorrect" }
    """
    try:
        data    = json.loads(request.body)
        card_id = data.get('card_id')
        result  = data.get('result')
 
        if not card_id or result not in ('correct', 'incorrect'):
            return JsonResponse(
                {'success': False, 'message': 'Неверные параметры'},
                status=400
            )
 
        user_dictionary = MyDictionary.objects.get(user=request.user)
        entry = DictionaryCard.objects.get(
            dictionary=user_dictionary,
            card_id=card_id
        )
 
        if result == 'correct':
            entry.mark_correct()    # times_correct++, times_viewed++, last_viewed=now
        else:
            entry.mark_incorrect()  # times_incorrect++, times_viewed++, last_viewed=now
 
        return JsonResponse({
            'success':         True,
            'times_correct':   entry.times_correct,
            'times_incorrect': entry.times_incorrect,
            'times_viewed':    entry.times_viewed,
        })
 
    except (MyDictionary.DoesNotExist, DictionaryCard.DoesNotExist):
        return JsonResponse(
            {'success': False, 'message': 'Запись не найдена'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': str(e)},
            status=500
        )
    
# Для выборки
@login_required
def quiz_session(request):
    """
    Тренажёр «Выбор ответа».
    - Вопросы берутся из личного словаря пользователя
    - Ложные варианты — из всей базы Card
    - Количество вопросов = min(кол-во карточек в словаре, 15)
    - Количество вариантов ответа = от 4 до 7 (зависит от размера базы)
    """
    try:
        user_dict = request.user.dictionary
    except MyDictionary.DoesNotExist:
        user_dict = MyDictionary.objects.create(user=request.user)
 
    user_cards = list(user_dict.cards.all())
 
    # Нужно минимум 4 карточки в словаре
    if len(user_cards) < 4:
        return render(request, 'trainer/quiz.html', {
            'cards_json':     '[]',
            'all_cards_json': '[]',
            'not_enough': True,
            'user_cards_count': len(user_cards),
        })
 
    def card_to_dict(card):
        audio_url = None
        if card.audio:
            audio_url = request.build_absolute_uri(card.audio.url)
        return {
            'id':            card.id,
            'hieroglyph':    card.hieroglyph,
            'transcription': card.transcription,
            'translate':     card.translate,
            'audio':         audio_url,
        }
 
    # Карточки пользователя — источник вопросов
    # Количество вопросов за сессию: min(кол-во карточек, 15)
    session_size = min(len(user_cards), 15)
    user_card_data = [card_to_dict(c) for c in user_cards]
 
    # Все карточки из базы — источник ложных вариантов
    all_cards = Card.objects.all()
    all_card_data = [card_to_dict(c) for c in all_cards]
 
    # Количество вариантов ответа зависит от размера базы:
    # база < 4  → недостаточно (уже обработано выше)
    # база 4-5  → 4 варианта
    # база 6-8  → 5 вариантов
    # база 9-12 → 6 вариантов
    # база 13+  → 7 вариантов
    total_in_db = len(all_card_data)
    if total_in_db <= 5:
        options_count = 4
    elif total_in_db <= 8:
        options_count = 5
    elif total_in_db <= 12:
        options_count = 6
    else:
        options_count = 7
 
    return render(request, 'trainer/quiz.html', {
        'cards_json':     json.dumps(user_card_data),
        'all_cards_json': json.dumps(all_card_data),
        'session_size':   session_size,
        'options_count':  options_count,
    })

# Для флэш карточек
def trainers_home(request):
    return render(request, 'trainer/trainers_home.html')

@login_required
def flashcards_session(request):
    # Получаем словарь текущего пользователя
    try:
        user_dict = request.user.dictionary          # related_name='dictionary'
    except MyDictionary.DoesNotExist:
        # если словарь по какой-то причине не создан — создаём
        user_dict = MyDictionary.objects.create(user=request.user)

    # Берём ВСЕ карточки из личного словаря пользователя
    cards = user_dict.cards.all().order_by('?')[:50]  # Случайные 50 из словаря пользователя
    # (через промежуточную модель DictionaryCard)
    # dict_cards = DictionaryCard.objects.filter(dictionary=user_dict)
    
    if not cards.exists():
        print("DEBUG cards:", card_data)
        return render(request, 'trainer/flashcards.html', {
            'cards_json': [],
            'debug_message': 'В вашем личном словаре пока нет карточек'
        })

    # Получаем связанные Card и нужные поля
    # cards = Card.objects.all()

     # можно убрать .order_by('?'), если хочешь стабильный порядок
    
    # Формируем данные для фронта
    card_data = []
    for card in cards:
        audio_url = None
        if card.audio:
            audio_url = request.build_absolute_uri(card.audio.url)

        card_data.append({
            'id': card.id,
            'hieroglyph': card.hieroglyph,
            'transcription': card.transcription,
            'translate': card.translate,
            'audio': audio_url,
        })

    return render(request, 'trainer/flashcards.html', { "cards": cards,
        'cards_json': json.dumps(card_data)
    })

class MyDictionaryPDFView(LoginRequiredMixin, View):
    def get(self, request):
        # Дублируем логику из MyDictionaryListView (без фильтров/поиска/сортировки для простоты)
        user_dictionary = request.user.dictionary
        cards = user_dictionary.cards.all()

        cards_with_info = []
        for card in cards:
            dict_entry = DictionaryCard.objects.get(dictionary=user_dictionary, card=card)
            card.dict_entry = dict_entry
            card.accuracy = dict_entry.get_accuracy()
            cards_with_info.append(card)

        context = {
            'total_cards': user_dictionary.get_cards_count(),
            'learned_cards': DictionaryCard.objects.filter(dictionary=user_dictionary, is_learned=True).count(),
            'not_learned_cards': DictionaryCard.objects.filter(dictionary=user_dictionary, is_learned=False).count(),
            'cards': cards_with_info,
        }

        html_string = render_to_string('trainer/my_dictionary_pdf.html', context)

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="my_dictionary_{date.today()}.pdf"'
            return response
        else:
            return HttpResponse("Ошибка генерации PDF", status=500)
        
def card_list(request):
    cards = Card.objects.all()
    
    paginator = Paginator(cards, 20)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(1)
    
    context = {'page_obj': page_obj}
    
    if request.user.is_authenticated:
        user_dict = request.user.dictionary
        in_dict_ids = set(
            DictionaryCard.objects.filter(dictionary=user_dict)
                                  .values_list('card_id', flat=True)
        )
        context['in_dict_ids'] = in_dict_ids
    
    return render(request, 'trainer/card_list.html', context)

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

@login_required
@require_POST
def add_to_dictionary(request):
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        
        if not card_id:
            return JsonResponse({'success': False, 'message': 'Нет ID карточки'}, status=400)
        
        card = Card.objects.get(id=card_id)
        dictionary = request.user.dictionary  # предполагаем, что есть related_name='dictionary'
        
        entry, created = DictionaryCard.objects.get_or_create(
            dictionary=dictionary,
            card=card
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Карточка добавлена в словарь'})
        else:
            return JsonResponse({'success': False, 'message': 'Карточка уже в словаре'})
            
    except Card.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Карточка не найдена'}, status=404)
    except MyDictionary.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Словарь пользователя не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_POST
def toggle_learned(request):
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        
        if not card_id:
            return JsonResponse({'success': False, 'message': 'Нет ID карточки'}, status=400)
        
        # Находим запись в словаре пользователя
        user_dictionary = MyDictionary.objects.get(user=request.user)
        entry = DictionaryCard.objects.get(
            dictionary=user_dictionary,
            card_id=card_id
        )
        
        # Меняем статус
        entry.is_learned = not entry.is_learned
        entry.save()
        
        return JsonResponse({
            'success': True,
            'is_learned': entry.is_learned,
            'message': 'Статус обновлён'
        })
        
    except (MyDictionary.DoesNotExist, DictionaryCard.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Запись не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_POST
def remove_from_dictionary(request):
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        
        if not card_id:
            return JsonResponse({'success': False, 'message': 'Нет ID карточки'}, status=400)
        
        user_dictionary = MyDictionary.objects.get(user=request.user)
        deleted, _ = DictionaryCard.objects.filter(
            dictionary=user_dictionary,
            card_id=card_id
        ).delete()
        
        if deleted:
            return JsonResponse({'success': True, 'message': 'Карточка удалена из словаря'})
        else:
            return JsonResponse({'success': False, 'message': 'Запись не найдена'}, status=404)
            
    except MyDictionary.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Словарь пользователя не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

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
    


