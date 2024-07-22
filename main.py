import asyncio
import datetime
import logging
import asyncpg


from apscheduler.schedulers.asyncio import AsyncIOScheduler


from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command


from datetime import datetime, timedelta

from core.handlers.basic import get_start, get_hello
from core.settings import settings
# from core.handlers.basic import get_start
from core.utils.commands import set_commands
# from core.middlewares.apschedulermiddleware import SchedulerMiddleware



logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
dp = Dispatcher()


@dp.startup()
async def start_bot():
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text='Бот запущен!')


@dp.shutdown()
async def stop_bot():
    await bot.send_message(settings.bots.admin_id, text='Бот остановлен!')




async def begin():
    # TODO: Register all functions


    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    # scheduler.add_job(apsched.send_message_time, trigger='date', run_date=datetime.now() + timedelta(seconds=10),
    #                   kwargs={'bot': bot, 'chat_id': dp.message.from_user.id})
    # scheduler.add_job(apsched.send_message_cron, trigger='cron', hour=datetime.now().hour,
    #                   minute=datetime.now().minute + 1, start_date=datetime.now(), kwargs={'bot': bot,  'chat_id':
    #         dp.message.from_user.id})
    # scheduler.add_job(apsched.send_message_interval, trigger='interval', seconds=60, kwargs={'bot': bot,  'chat_id':
    #     dp.message.from_user.id})
    scheduler.start()


    # dp.update.middleware.register(SchedulerMiddleware(scheduler))


    dp.message.register(get_start, Command('start'))
    dp.message.register(get_hello, F.text == 'Привет')


    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(begin())
