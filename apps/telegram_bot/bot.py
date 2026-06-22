import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, CallbackQueryHandler
)
from django.conf import settings
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import TelegramUser
from apps.bookings.models import Booking, BookingStatus
from datetime import datetime, timedelta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

User = get_user_model()


class CottageBookingBot:    
    def __init__(self):
        self.token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не настроен в settings.py")
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("bookings", self.bookings_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        logger.debug(f"User {user.id} ({user.first_name}) trying to access bot")
        
        telegram_user = await self._register_telegram_user(user)
        if not telegram_user:
            await update.message.reply_text(
                "❌ Ошибка регистрации!\n\n"
                "Не удалось создать аккаунт. Обратитесь к администратору."
            )
            return
        
        is_staff = await self._is_staff_member(user.id)
        logger.debug(f"Is staff check result: {is_staff}")
        
        if not is_staff:
            logger.debug(f"Access denied for user {user.id}")
            await update.message.reply_text(
                "❌ Доступ ограничен!\n\n"
                "Ваш аккаунт зарегистрирован, но у вас нет прав персонала.\n"
                "Для получения доступа обратитесь к администратору.\n\n"
                "Администратор может предоставить вам доступ через админ-панель."
            )
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("📋 Бронирования", callback_data="bookings")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"👋 Добро пожаловать, {user.first_name}!\n\n"
            "🤖 Я бот для уведомлений о бронированиях коттеджей.\n"
            "Я буду отправлять вам уведомления о:\n"
            "• 🆕 Новых бронированиях\n"
            "• 🔄 Изменениях статуса\n"
            "• ❌ Отменах бронирований\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = """
🤖 **Команды бота:**

/start - Запуск бота и регистрация
/help - Показать это сообщение
/stats - Статистика бронирований
/bookings - Список активных бронирований
/subscribe - Подписаться на уведомления
/unsubscribe - Отписаться от уведомлений

📱 **Уведомления:**
• Новые бронирования
• Изменения статуса
• Отмены бронирований
• Ежедневная статистика

❓ **Поддержка:**
Если у вас есть вопросы, обратитесь к администратору системы.
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._is_staff_member(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещен!")
            return
        
        stats = await self._get_booking_stats()
        await update.message.reply_text(stats, parse_mode='Markdown')
    
    async def bookings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._is_staff_member(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещен!")
            return
        
        bookings = await self._get_recent_bookings()
        await update.message.reply_text(bookings, parse_mode='Markdown')
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._is_staff_member(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещен!")
            return
        
        telegram_user = await self._register_telegram_user(update.effective_user)
        if telegram_user:
            await update.message.reply_text("✅ Вы успешно подписались на уведомления!")
        else:
            await update.message.reply_text(
                "❌ Ошибка при подписке!\n\n"
                "Ваш аккаунт не зарегистрирован в системе.\n"
                "Обратитесь к администратору для получения доступа."
            )
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._is_staff_member(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещен!")
            return
        
        try:
            telegram_user = TelegramUser.objects.get(telegram_id=update.effective_user.id)
            telegram_user.is_active = False
            telegram_user.save()
            await update.message.reply_text("✅ Вы отписались от уведомлений.")
        except TelegramUser.DoesNotExist:
            await update.message.reply_text("❌ Вы не были подписаны на уведомления.")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "stats":
            stats = await self._get_booking_stats()
            await query.edit_message_text(stats, parse_mode='Markdown')
        elif query.data == "bookings":
            bookings = await self._get_recent_bookings()
            await query.edit_message_text(bookings, parse_mode='Markdown')
        elif query.data == "help":
            await self.help_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Я понимаю только команды. Используйте /help для списка доступных команд."
        )
    
    async def _is_staff_member(self, telegram_id: int) -> bool:
        from asgiref.sync import sync_to_async
        
        @sync_to_async
        def check_staff():
            try:
                telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
                logger.debug(f"Found TelegramUser {telegram_id}, is_staff: {telegram_user.user.is_staff}")
                logger.debug(f"User email: {telegram_user.user.email}")
                return telegram_user.user.is_staff or telegram_user.user.is_superuser
            except TelegramUser.DoesNotExist:
                logger.debug(f"TelegramUser {telegram_id} not found in database")
                return False
        
        return await check_staff()
    
    async def _register_telegram_user(self, telegram_user) -> TelegramUser:
        from asgiref.sync import sync_to_async
        
        @sync_to_async
        def create_or_activate_user():
            try:
                tg_user = TelegramUser.objects.get(telegram_id=telegram_user.id)
                logger.debug(f"Activating existing TelegramUser {telegram_user.id}")
                tg_user.is_active = True
                tg_user.save()
                return tg_user
            except TelegramUser.DoesNotExist:
                logger.debug(f"Creating new TelegramUser {telegram_user.id} WITHOUT staff privileges")
                
                logger.debug(f"About to create user with is_staff=False")
                user = User.objects.create(
                    username=f"tg_{telegram_user.id}",
                    email=f"tg_{telegram_user.id}@example.com",
                    first_name=telegram_user.first_name or '',
                    last_name=telegram_user.last_name or '',
                    is_staff=False,
                    is_superuser=False,
                    is_active=True
                )
                
                logger.debug(f"User created! username={user.username}, is_staff={user.is_staff}, is_superuser={user.is_superuser}")
                
                user_from_db = User.objects.get(id=user.id)
                logger.debug(f"User from DB: username={user_from_db.username}, is_staff={user_from_db.is_staff}, is_superuser={user_from_db.is_superuser}")
                
                tg_user = TelegramUser.objects.create(
                    user=user,
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    is_active=True
                )
                return tg_user
        
        return await create_or_activate_user()
    
    async def _get_booking_stats(self) -> str:
        from asgiref.sync import sync_to_async
        
        @sync_to_async
        def get_stats():
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            total_bookings = Booking.objects.count()
            pending_bookings = Booking.objects.filter(status=BookingStatus.PENDING).count()
            confirmed_bookings = Booking.objects.filter(status=BookingStatus.CONFIRMED).count()
            recent_bookings = Booking.objects.filter(created_at__gte=week_ago).count()
            
            return f"""
📊 **Статистика бронирований**

📅 **Общая статистика:**
• Всего бронирований: {total_bookings}
• Ожидают подтверждения: {pending_bookings}
• Подтверждены: {confirmed_bookings}

📈 **За последнюю неделю:**
• Новых бронирований: {recent_bookings}

🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}
            """
        
        return await get_stats()
    
    async def _get_recent_bookings(self) -> str:
        from asgiref.sync import sync_to_async
        
        @sync_to_async
        def get_bookings():
            recent_bookings = Booking.objects.select_related('user', 'cottage').order_by('-created_at')[:10]
            
            if not recent_bookings:
                return "📋 **Последние бронирования**\n\nНет активных бронирований."
            
            bookings_text = "📋 **Последние бронирования:**\n\n"
            
            for booking in recent_bookings:
                status_emoji = {
                    BookingStatus.PENDING: "⏳",
                    BookingStatus.CONFIRMED: "✅",
                    BookingStatus.CANCELLED: "❌",
                    BookingStatus.COMPLETED: "🏁"
                }.get(booking.status, "❓")
                
                bookings_text += f"""
{status_emoji} **{booking.cottage.name}**
👤 {booking.user.get_full_name() or booking.user.email}
📅 {booking.check_in} - {booking.check_out} ({booking.nights} ночей)
👥 {booking.guests} гостей
💰 {booking.total_price} ₽
📝 Статус: {booking.get_status_display()}
---
                """
            
            return bookings_text
        
        return await get_bookings()
    
    async def send_booking_notification(self, booking: Booking, notification_type: str = "new"):
        from asgiref.sync import sync_to_async
        
        logger.info(f"Starting notification send: {notification_type}")
        
        @sync_to_async
        def get_active_users():
            users = list(TelegramUser.objects.filter(is_active=True))
            logger.info(f"Found active users: {len(users)}")
            return users
        
        active_users = await get_active_users()
        
        if not active_users:
            logger.warning("No active users for notifications")
            return
        
        if notification_type == "new":
            message = self._format_new_booking_message(booking)
        elif notification_type == "status_change":
            message = self._format_status_change_message(booking)
        elif notification_type == "cancelled":
            message = self._format_cancelled_booking_message(booking)
        else:
            logger.error(f"Unknown notification type: {notification_type}")
            return
        
        logger.debug(f"Message to send:\n{message[:100]}...")
        
        sent_count = 0
        for tg_user in active_users:
            try:
                logger.debug(f"Sending message to user {tg_user.telegram_id}")
                await self.application.bot.send_message(
                    chat_id=tg_user.telegram_id,
                    text=message,
                    parse_mode='Markdown'
                )
                sent_count += 1
                logger.info(f"Message sent to user {tg_user.telegram_id}")
            except Exception as e:
                logger.error(f"Error sending message to user {tg_user.telegram_id}: {e}")
                logger.error(f"Error sending message to user {tg_user.telegram_id}: {e}")
        
        logger.info(f"Sent {sent_count} of {len(active_users)} notifications")
    
    def _format_new_booking_message(self, booking: Booking) -> str:
        return f"""
🆕 **Новое бронирование!**

👤 **Клиент:** {booking.user.get_full_name() or booking.user.email}
📞 **Телефон:** {booking.user.phone or 'Не указан'}
🏠 **Коттедж:** {booking.cottage.name}
📅 **Даты:** {booking.check_in} - {booking.check_out} ({booking.nights} ночей)
👥 **Гости:** {booking.guests} человек
💰 **Стоимость:** {booking.total_price} ₽
📝 **Пожелания:** {booking.special_requests or 'Нет'}

⏰ **Создано:** {booking.created_at.strftime('%d.%m.%Y %H:%M')}
        """
    
    def _format_status_change_message(self, booking: Booking) -> str:
        """Форматирует сообщение об изменении статуса"""
        return f"""
🔄 **Изменение статуса бронирования**

🏠 **Коттедж:** {booking.cottage.name}
👤 **Клиент:** {booking.user.get_full_name() or booking.user.email}
📅 **Даты:** {booking.check_in} - {booking.check_out}

📝 **Новый статус:** {booking.get_status_display()}
        """
    
    def _format_cancelled_booking_message(self, booking: Booking) -> str:
        cottage_name = getattr(booking.cottage, 'name', 'Неизвестный коттедж')
        user_name = getattr(booking.user, 'get_full_name', lambda: None)() or getattr(booking.user, 'email', 'Неизвестный пользователь')
        
        return f"""
❌ **Отмена бронирования**

🏠 **Коттедж:** {cottage_name}
👤 **Клиент:** {user_name}
📅 **Даты:** {booking.check_in} - {booking.check_out}
        """
    
    def run(self):
        """Запускает бота"""
        logger.info("Starting Telegram bot...")
        self.application.run_polling()


bot_instance = None


def get_bot():
    global bot_instance
    if bot_instance is None:
        bot_instance = CottageBookingBot()
    return bot_instance


async def send_callback_notification(callback_request):
    try:
        # Получаем активных пользователей с правами персонала
        active_users = await sync_to_async(list)(
            TelegramUser.objects.filter(
                is_active=True,
                user__is_staff=True
            ).select_related('user')
        )
        
        if not active_users:
            logger.warning("No active staff users found for callback notification")
            return False
        
        message = _format_callback_message(callback_request)
        
        bot = get_bot()
        
        sent_count = 0
        for telegram_user in active_users:
            try:
                await bot.application.bot.send_message(
                    chat_id=telegram_user.telegram_id,
                    text=message,
                    parse_mode='HTML'
                )
                sent_count += 1
                logger.info(f"Callback notification sent to user {telegram_user.telegram_id}")
            except Exception as e:
                logger.error(f"Failed to send callback notification to {telegram_user.telegram_id}: {e}")
        
        logger.info(f"Sent {sent_count} callback notifications")
        return sent_count > 0
        
    except Exception as e:
        logger.error(f"Error sending callback notification: {e}")
        return False


def _format_callback_message(callback_request):
    cottage_info = ""
    if callback_request.cottage:
        cottage_info = f"\n🏠 <b>Коттедж:</b> {callback_request.cottage.name}\n💰 <b>Цена:</b> {callback_request.cottage.price_per_night} ₽/ночь"
    
    preferred_time = ""
    if callback_request.preferred_time:
        preferred_time = f"\n⏰ <b>Удобное время:</b> {callback_request.preferred_time}"
    
    message = f"""
🔔 <b>НОВАЯ ЗАЯВКА НА ОБРАТНЫЙ ЗВОНОК</b>

👤 <b>Клиент:</b> {callback_request.full_name}
📞 <b>Телефон:</b> {callback_request.phone}
📧 <b>Email:</b> {callback_request.email or 'Не указан'}{cottage_info}{preferred_time}

💬 <b>Сообщение:</b>
{callback_request.message or 'Не указано'}

📅 <b>Дата заявки:</b> {callback_request.created_at.strftime('%d.%m.%Y %H:%M')}
🆔 <b>ID заявки:</b> #{callback_request.id}
"""
    
    return message
