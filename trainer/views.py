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
    