import telebot
import requests
from telebot import types
from environs import Env

env = Env()
env.read_env()

bot_token = env('TELEGRAM_TOKEN')
bot = telebot.TeleBot(bot_token)
api_url = env('API_URL')


@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text='Узнать погоду')
    keyboard_markup.add(button)
    bot.send_message(message.chat.id, 'Привет! Я бот для получения погоды. Нажмите кнопку Узнать погоду для начала.',
                     reply_markup=keyboard_markup)


@bot.message_handler(func=lambda message: True)
def weather_request(message):
    if message.text == 'Узнать погоду':
        msg = bot.send_message(message.chat.id, 'Введите название города (на русском или английском)')
        bot.register_next_step_handler(msg, get_weather_from_api)
    else:
        bot.send_message(message.chat.id, 'Используйте кнопки для взаимодействия')


def get_weather_from_api(message):
    city = message.text
    payload = {'city': city}
    response = requests.get(api_url, params=payload)

    if response.status_code == 200:
        weather_data = response.json()

        if 'error' in weather_data:
            bot.send_message(message.chat.id, f'Произошла ошибка: {weather_data["error"]}')
        else:
            mess = (f'Сейчас погода в городе {city}:\n'
                       f'Температура: {weather_data["temperature"]}°C\n'
                       f'Давление: {weather_data["pressure"]} мм рт. ст.\n'
                       f'Скорость ветра: {weather_data["wind_speed"]} м/c')
            bot.send_message(message.chat.id, mess)
    else:
        bot.send_message(message.chat.id, 'Ошибка при получении данных о погоде')


bot.polling(none_stop=True)
