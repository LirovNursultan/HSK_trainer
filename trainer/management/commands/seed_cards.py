# seeder.py или manage/commands/seed_cards.py

import json
import os
from django.core.management.base import BaseCommand
from trainer.models import Card  # Замените your_app на название вашего приложения

class Command(BaseCommand):
    help = 'Импортирует HSK карточки из JSON файла'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Путь к JSON файлу с карточками'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все существующие карточки перед импортом'
        )
    
    def handle(self, *args, **options):
        json_file = options['json_file']
        
        # Проверка существования файла
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'Файл "{json_file}" не найден')
            )
            return
        
        # Опциональное удаление существующих данных
        if options['clear']:
            count_deleted, _ = Card.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Удалено {count_deleted} карточек')
            )
        
        try:
            # Загрузка JSON файла
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.stdout.write(f'Загружено {len(data)} записей из JSON')
            
            # Счетчики
            created_count = 0
            skipped_count = 0
            
            # Итерация по данным
            for item in data:
                try:
                    # Получить переводы
                    translations = item.get('translations', {})
                    
                    # Приоритет: русский перевод, потом английский
                    rus_translations = translations.get('rus', [])
                    eng_translations = translations.get('eng', [])
                    
                    # Выбрать первый доступный перевод
                    translate = ''
                    if rus_translations:
                        translate = rus_translations[0]
                    elif eng_translations:
                        translate = eng_translations[0]
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Пропущено {item.get("hanzi", "?")} - нет переводов'
                            )
                        )
                        skipped_count += 1
                        continue
                    
                    # Получить данные
                    hanzi = item.get('hanzi', '')
                    transcription = item.get('pinyin', '')
                    
                    if not hanzi or not transcription:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Пропущено - отсутствуют hanzi или pinyin'
                            )
                        )
                        skipped_count += 1
                        continue
                    
                    # Создать или обновить карточку
                    card, created = Card.objects.update_or_create(
                        hieroglyph=hanzi,
                        defaults={
                            'translate': translate,
                            'transcription': transcription,
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Создана: {hanzi} - {translate}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'✓ Обновлена: {hanzi} - {translate}')
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Ошибка при обработке {item.get("hanzi", "?")}: {str(e)}'
                        )
                    )
                    skipped_count += 1
            
            # Итоговой вывод
            self.stdout.write(self.style.SUCCESS('\n' + '='*50))
            self.stdout.write(self.style.SUCCESS(f'Создано: {created_count}'))
            self.stdout.write(self.style.SUCCESS(f'Пропущено: {skipped_count}'))
            self.stdout.write(self.style.SUCCESS('='*50))
            self.stdout.write(self.style.SUCCESS('Импорт завершен успешно!'))
        
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Ошибка: файл не является корректным JSON')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Неожиданная ошибка: {str(e)}')
            )