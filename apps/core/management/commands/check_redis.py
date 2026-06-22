from django.core.management.base import BaseCommand
from django.core.cache import cache
from django_redis.exceptions import ConnectionInterrupted
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Проверяет статус Redis и автоматически исправляет проблемы'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Проверка Redis...')
        
        # Получаем клиент Redis напрямую
        try:
            from django_redis import get_redis_connection
            redis_client = get_redis_connection("default")
            
            # Проверяем роль Redis
            info = redis_client.info('replication')
            role = info.get('role', 'unknown')
            
            if role == 'slave' or role == 'replica':
                self.stdout.write(self.style.WARNING(
                    f'⚠️  Redis в режиме {role}! Переводим в master...'
                ))
                
                # Пытаемся перевести в master
                try:
                    redis_client.slaveof(None, None)
                    self.stdout.write(self.style.SUCCESS('✅ Redis переведен в режим master'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'❌ Ошибка при переводе в master: {e}'
                    ))
                    self.stdout.write(self.style.WARNING(
                        '💡 Выполните вручную: docker compose exec redis redis-cli SLAVEOF NO ONE'
                    ))
                    return
                
                # Проверяем еще раз
                info = redis_client.info('replication')
                role = info.get('role', 'unknown')
            
            if role == 'master':
                self.stdout.write(self.style.SUCCESS('✅ Redis в режиме master'))
                
                # Проверяем возможность записи
                try:
                    cache.set('health_check', 'ok', 10)
                    result = cache.get('health_check')
                    if result == 'ok':
                        cache.delete('health_check')
                        self.stdout.write(self.style.SUCCESS('✅ Redis может писать данные'))
                    else:
                        self.stdout.write(self.style.WARNING('⚠️  Redis не может читать данные'))
                except (ConnectionInterrupted, Exception) as e:
                    self.stdout.write(self.style.ERROR(
                        f'❌ Ошибка записи в Redis: {e}'
                    ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'❌ Неизвестная роль Redis: {role}'
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'❌ Ошибка подключения к Redis: {e}'
            ))
            logger.error(f'Redis check failed: {e}')

