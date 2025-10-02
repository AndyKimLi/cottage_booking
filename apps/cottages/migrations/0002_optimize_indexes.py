from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cottages', '0001_initial'),
    ]

    operations = [
        # Индексы для оптимизации запросов коттеджей
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cottage_is_available ON cottages_cottage(is_available);",
            reverse_sql="DROP INDEX IF EXISTS idx_cottage_is_available;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cottage_price ON cottages_cottage(price_per_night);",
            reverse_sql="DROP INDEX IF EXISTS idx_cottage_price;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cottage_capacity ON cottages_cottage(max_guests);",
            reverse_sql="DROP INDEX IF EXISTS idx_cottage_capacity;"
        ),
        # Составной индекс для фильтрации
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cottage_filter ON cottages_cottage(is_available, max_guests, price_per_night);",
            reverse_sql="DROP INDEX IF EXISTS idx_cottage_filter;"
        ),
    ]
