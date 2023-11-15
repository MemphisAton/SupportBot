import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers import user_handlers
from untils import until


# начало работы бота
async def main():
    logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения
    # Инициализируем бот и диспетчер
    bot: Bot = Bot(until.config.tg_bot.token,
                   parse_mode="HTML")  # Создаем объекты бота и указываем форматирование, parse_mode=None если отменить
    dp: Dispatcher = Dispatcher()
    dp.include_router(user_handlers.rt)  # Регистриуем роутер в диспетчере, если модулей много, регистрируем роут из каждого
    await bot.delete_webhook(drop_pending_updates=True)  # пропускаем сообщения сделаные до старта бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
