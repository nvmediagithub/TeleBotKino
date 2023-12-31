import requests
from telebot.types import ReplyKeyboardMarkup
import telebot

API_URL = 'https://api.kinopoisk.dev/v1.4/movie/random'
API_TOKEN = ''
TELEGRAM_TOKEN = ''
ADMINISTRATOR_ID = 'ID АДМИНИСТРАТОРА'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add('Случайный фильм')
keyboard.add('Оставить отзыв')


@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text='Я КиноБот. Нажми кнопку «Случайный фильм» и я пришлю тебе фильм!',
        reply_markup=keyboard
    )


@bot.message_handler(content_types=['text'])
def get_text(message):
    print(message.text)
    if message.text == 'Случайный фильм':
        movie_poster, movie_text = get_random_movie()
        bot.send_photo(
            chat_id=message.chat.id,
            photo=movie_poster,
            caption=movie_text,
            reply_markup=keyboard
        )
    elif message.text == 'Оставить отзыв':
        msg = bot.send_message(message.chat.id, 'Введите текст отзыва:')
        bot.register_next_step_handler(msg, get_review)


def get_random_movie():
    response = requests.get(API_URL, params={
        "notNullFields": [
            "poster.url"
        ]
    }, headers={
        'X-API-KEY': API_TOKEN
    })
    response.encoding = 'utf-8'
    print(response.text)
    random_movie = response.json()
    movie_text = f'🎬 Фильм: {random_movie["names"][0]["name"]}\n\n'
    movie_text += f'{random_movie["description"]}\n\n'
    movie_text += f'👀 Рейтинг на кинопоиске: {random_movie["rating"]["kp"]}\n'
    genres = []
    for genre in random_movie['genres']:
        genres.append(genre['name'])
    movie_text += f'👏 Жанры: {", ".join(genres)}\n'
    if 'videos' in random_movie:
        if 'trailers' in random_movie:
            movie_text += f'⏯️ Трейлер: {random_movie["videos"]["trailers"][-1]["url"]}'
        elif 'teasers' in random_movie:
            movie_text += f'📺 *Трейлер:* {random_movie["videos"]["teasers"][-1]["url"]}'
    print(random_movie)
    movie_poster = random_movie['poster']['url']
    return movie_poster, movie_text


def get_review(msg):
    # kost
    ADMINISTRATOR_ID = msg.chat.id
    bot.send_message(ADMINISTRATOR_ID, msg.text)
    bot.send_message(msg.chat.id, 'Отзыв отправлен.', reply_markup=keyboard)


bot.infinity_polling()
