from django.core.management.base import BaseCommand
from apps.telegram_bot.bot import get_bot


class Command(BaseCommand):
    help = 'Запускает Telegram бота для уведомлений персонала'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Запуск Telegram бота...')
        )
        
        try:
            bot = get_bot()
            bot.run()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Бот остановлен пользователем')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка запуска бота: {e}')
            )
