import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

API_TOKEN = '6569216429:AAFi-u_8GWjdJNoPpZVRiNe3M8o-rfUnXFI'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def setup_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def parse_yandex_market(query):
    driver = setup_selenium()
    driver.get(f'https://market.yandex.ru/search?text={query}')
    products = driver.find_elements(By.CSS_SELECTOR, '.n-snippet-card2__title')
    results = []
    for product in products[:5]:  # Получаем первые 5 результатов
        title = product.text
        link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
        results.append(f'{title}\n{link}')
    driver.quit()
    return '\n\n'.join(results)

@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне название товара, и я найду его на Яндекс Маркете.")

@dp.message()
async def handle_message(message: types.Message):
    query = message.text
    await message.reply("Ищу товар на Яндекс Маркете...")
    result = parse_yandex_market(query)
    await message.reply(result if result else "Не удалось найти товар.")

async def begin():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()



if __name__ == '__main__':
    asyncio.run(begin())

