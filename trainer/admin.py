from django.contrib import admin
from .models import Card, DictionaryCard, MyDictionary

admin.site.register(Card)

admin.site.register(MyDictionary)
admin.site.register(DictionaryCard)
