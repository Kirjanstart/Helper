import logging
import lxml
import requests
import asyncio
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import certifi



API_TOKEN = ''

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def fetch_page(url):
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)  # Используем certifi для проверки SSL
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def parse_yandex_market():
    url = 'https://market.yandex.ru/catalog--skidki/23253665'
    page = fetch_page(url)
    if not page:
        return []
    soup = BeautifulSoup(page, 'lxml')

    discounts = []
    items = soup.find_all('div', class_='n-snippet-cell2__content')

    for item in items:
        try:
            title = item.find('div', class_='n-snippet-cell2__title').text.strip()
            old_price = item.find('span', class_='price-old').text.strip()
            new_price = item.find('span', class_='price').text.strip()
            discount = {
                'title': title,
                'old_price': old_price,
                'new_price': new_price
            }
            discounts.append(discount)
        except AttributeError:
            continue

    return discounts

def parse_megamarket():
    url = 'https://megamarket.com/discounts'
    page = fetch_page(url)
    if not page:
        return []
    soup = BeautifulSoup(page, 'lxml')

    discounts = []
    items = soup.find_all('div', class_='product-card')

    for item in items:
        try:
            title = item.find('h3', class_='product-card__title').text.strip()
            old_price = item.find('span', class_='product-card__old-price').text.strip()
            new_price = item.find('span', class_='product-card__price').text.strip()
            discount = {
                'title': title,
                'old_price': old_price,
                'new_price': new_price
            }
            discounts.append(discount)
        except AttributeError:
            continue

    return discounts

def parse_ozon():
    url = 'https://www.ozon.ru/highlight/sales/'
    page = fetch_page(url)
    if not page:
        return []
    soup = BeautifulSoup(page, 'lxml')

    discounts = []
    items = soup.find_all('div', class_='a0c4')

    for item in items:
        try:
            title = item.find('a', class_='tile-hover-target').text.strip()
            old_price = item.find('span', class_='ui-a2').text.strip()
            new_price = item.find('span', class_='ui-a2').next_sibling.text.strip()
            discount = {
                'title': title,
                'old_price': old_price,
                'new_price': new_price
            }
            discounts.append(discount)
        except AttributeError:
            continue

    return discounts

def parse_aliexpress():
    url = 'https://www.aliexpress.com/category/100003109/deals'
    page = fetch_page(url)
    if not page:
        return []
    soup = BeautifulSoup(page, 'lxml')

    discounts = []
    items = soup.find_all('div', class_='item')

    for item in items:
        try:
            title = item.find('h3', class_='title').text.strip()
            old_price = item.find('span', class_='price-old').text.strip()
            new_price = item.find('span', class_='price-current').text.strip()
            discount = {
                'title': title,
                'old_price': old_price,
                'new_price': new_price
            }
            discounts.append(discount)
        except AttributeError:
            continue

    return discounts

def parse_wildberries():
    url = 'https://www.wildberries.ru/promotions'
    page = fetch_page(url)
    if not page:
        return []
    soup = BeautifulSoup(page, 'lxml')

    discounts = []
    items = soup.find_all('div', class_='sale-item')

    for item in items:
        try:
            title = item.find('span', class_='goods-name').text.strip()
            old_price = item.find('span', class_='old-price').text.strip()
            new_price = item.find('span', class_='sale-price').text.strip()
            discount = {
                'title': title,
                'old_price': old_price,
                'new_price': new_price
            }
            discounts.append(discount)
        except AttributeError:
            continue

    return discounts

def parse_discounts():
    discounts = []
    discounts.extend(parse_yandex_market())
    discounts.extend(parse_megamarket())
    discounts.extend(parse_ozon())
    discounts.extend(parse_aliexpress())
    discounts.extend(parse_wildberries())

    discounts.sort(key=lambda x: float(x['old_price'].replace('₽', '').replace(',', '')) - float(x['new_price'].replace('₽', '').replace(',', '')), reverse=True)
    return discounts[:10]

top_discounts = []

async def update_discounts():
    global top_discounts
    top_discounts = parse_discounts()
    logging.info("Updated discounts")

@dp.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот, который поможет тебе найти лучшие скидки. Используй команду /discounts, чтобы получить лучшие скидки на сегодня.")

@dp.message(Command(commands=['discounts']))
async def send_discounts(message: types.Message):
    if not top_discounts:
        await update_discounts()

    response = "Топ 10 скидок на сегодня:\n\n"
    for discount in top_discounts:
        response += f"{discount['title']}\nСтарая цена: {discount['old_price']}\nНовая цена: {discount['new_price']}\n\n"

    await message.answer(response, parse_mode=ParseMode.MARKDOWN)

@dp.message()
async def echo(message: types.Message):
    await message.answer("Я не понимаю эту команду. Используй /discounts, чтобы получить лучшие скидки.")

async def begin():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()



if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_discounts, 'interval', hours=24)
    scheduler.start()
    asyncio.run(begin())


