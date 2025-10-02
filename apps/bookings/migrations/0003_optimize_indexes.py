from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_booking_guest_email_booking_guest_name_and_more'),
    ]

    operations = [
        # Индексы для оптимизации запросов
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_booking_user_id ON bookings_booking(user_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_booking_user_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_booking_cottage_id ON bookings_booking(cottage_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_booking_cottage_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_booking_status ON bookings_booking(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_booking_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_booking_check_in ON bookings_booking(check_in);",
            reverse_sql="DROP INDEX IF EXISTS idx_booking_check_in;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_booking_check_out ON bookings_booking(check_out);",
            reverse_sql="DROP INDEX IF EXISTS idx_booking_check_out;"
        ),
        # Составной индекс для поиска по датам
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_booking_dates ON bookings_booking(check_in, check_out);",
            reverse_sql="DROP INDEX IF EXISTS idx_booking_dates;"
        ),
    ]
