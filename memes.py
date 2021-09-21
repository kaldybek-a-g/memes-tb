import telebot
import sqlite3
import const
from fuzzywuzzy import fuzz
from telebot import types

def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(const.API_TOKEN)
# bot.set_update_listener(listener)
# connection = sqlite3.connect('memes.db')
# cursor = connection.cursor()


class User:
    def __init__(self):
        self.name = None
        self.email = None
        self.phone_num = None
        self.country = None

    def __repr__(self):
        return str(self.__dict__)


user_data = {}


def selelect_user_info(user_id):
    connect = sqlite3.connect('memes.db')
    cursor = connect.cursor()
    user_info = cursor.execute("SELECT * FROM customers WHERE id_customer = :0", {'0': user_id}).fetchone()
    connect.close()
    return user_info


@bot.message_handler(func=lambda msg: True if not selelect_user_info(msg.chat.id) else False)
def send_welcome(message):
    bot.send_message(message.chat.id, 'Доброго времени суток! 😊 Можно узнать Ваше имя?')
    bot.register_next_step_handler(message, register_user_name_message)


def register_user_name_message(message):
    user = User()
    user.name = message.text
    user_data[message.chat.id] = user
    bot.send_message(message.chat.id, "Отлично, теперь введите пожалуйста Вашу почту ✉️:")
    bot.register_next_step_handler(message, register_user_email_message)


def register_user_email_message(message):
    # TODO: Добавить валидацию почты
    user = user_data[message.chat.id]
    user.email = message.text
    bot.send_message(message.chat.id, "Введите Ваш номер телефона 📞:")
    bot.register_next_step_handler(message, register_user_phone_num_message)


def register_user_phone_num_message(message):
    # TODO: Добавить валидацию номера телефона
    user = user_data[message.chat.id]
    user.phone_num = message.text.replace("+", "")

    connect = sqlite3.connect('memes.db')
    cursor = connect.cursor()
    cursor.execute("INSERT INTO customers VALUES (:0, :1, :2, :3, :4, :5)", {'0': message.chat.id, '1': user.name, '2': user.phone_num, '3': user.email, '4': None, '5': None})
    connect.commit()
    connect.close()

    bot.send_message(message.chat.id, "Отлично, Ваши данные успешно зарегистрированы 💻")
    hello(message)

@bot.message_handler(commands=['start', 'help'])
def hello(message):
    user_name = selelect_user_info(message.chat.id)[1]
    bot.send_message(message.chat.id, f'Приятно с Вами познакомится, {user_name} '
                                      ' Вас приветствует MEMES 👻 магазин компьютерных игр 🎮')
    choose_country = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    kz = types.InlineKeyboardButton(text='Казахстан 🇰🇿', callback_data='kz')
    ru = types.InlineKeyboardButton(text='Россия 🇷🇺', callback_data='ru')
    usa = types.InlineKeyboardButton(text='Беларусь 🇧🇾', callback_data='by')
    choose_country.add(kz, ru, usa)
    bot.send_message(message.chat.id,
                     "Предупреждение! 📌 Мы продаем компьютерные игры только в странах, которые приведены ниже, выберите страну: ",
                     reply_markup=choose_country)
    bot.register_next_step_handler(message, ask_user_country)

def ask_user_country(message):
    print(message.text)
    countries = ["Казахстан 🇰🇿",
                 "Россия 🇷🇺",
                 "Беларусь 🇧🇾"]
    if message.text in countries:
        connect = sqlite3.connect('memes.db')
        cursor = connect.cursor()
        cursor.execute("UPDATE customers set country =:country WHERE id_customer =:id", {"country":message.text,"id":message.chat.id})
        connect.commit()
        connect.close()
        bot.send_message(message.chat.id, "Укажите Ваш возраст: ")
        bot.register_next_step_handler(message, ask_user_age)
    else:
        bot.send_message(message.chat.id, "Извините, но мы не производим продажу игр в других странах, кроме Казахстана, Росссии и Беларусь")
def ask_user_age(message):
    if message.text.isnumeric() and 18<= int(message.text) <=100:
        connect = sqlite3.connect('memes.db')
        cursor = connect.cursor()
        cursor.execute("UPDATE customers set age =:age WHERE id_customer =:id", {"age":message.text,"id": message.chat.id})
        connect.commit()
        connect.close()
        bot.send_message(message.chat.id,"Отлично, приятных покупок! 🛍", reply_markup=markup_menu)
    else:
        bot.send_message(message.chat.id, "Извините, но мы не продаем компьютерные игры лицам, младше 18 лет 📌")
        bot.send_message(message.chat.id, "Укажите Ваш возраст: ")
    print(message.text)


choose_country = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn_1 = types.KeyboardButton('🎮 Каталог')
btn_2 = types.KeyboardButton('👾 О нас')
btn_3 = types.KeyboardButton('🛒 Корзина')
btn_4 = types.KeyboardButton('💳 💸 Оплатить')
btn_5 = types.KeyboardButton('👻 Официальный сайт')
markup_menu.add(btn_1, btn_2, btn_3, btn_4, btn_5)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "👾 О нас":
        onas = types.InlineKeyboardMarkup(row_width=1)
        contacts = types.InlineKeyboardButton(text="Контакты", callback_data="contact")
        url_button = types.InlineKeyboardButton(text="Перейти в Instagram",
                                                url="https://www.instagram.com/memes_company___/")
        onas.add(url_button, contacts)
        bot.reply_to(message, "Выберите кнопку", reply_markup=onas)
    elif message.text == "💳 💸 Оплатить":
        # money = types.InlineKeyboardMarkup(row_width=1)
        # card = types.InlineKeyboardButton(text="💳 Безналичный рассчет", callback_data="card")
        # perevod = types.InlineKeyboardButton(text="💸 Перевод банковской картой", callback_data="perevod")
        # money.add(card, perevod)
        # bot.reply_to(message, "Выберите способ оплаты", reply_markup=money)
        connect = sqlite3.connect('memes.db')
        cursor = connect.cursor()
        data = cursor.execute(
            "SELECT COUNT(*), SUM (game.price) FROM basket INNER JOIN game ON basket.id_game= game.id_game WHERE id_customer=:id_customer ",
            {'id_customer': message.chat.id}).fetchone()
        cursor.execute("INSERT INTO purchases (id_customer,id_game) SELECT id_customer,id_game FROM basket WHERE id_customer=:id_customer ",  {'id_customer': message.chat.id})
        cursor.execute("DELETE FROM basket WHERE id_customer=:id_customer", {'id_customer': message.chat.id})
        connect.commit()
        connect.close()
        bot.send_message(message.chat.id, f"Оплачено, количество игр: {data[0]}, итог: {data[1]} $")
    elif message.text == "👻 Официальный сайт":
        cite = types.InlineKeyboardMarkup(row_width=1)
        url_b = types.InlineKeyboardButton(text="Перейти на сайт",
                                                url="http://memes_shop2.tilda.ws/")
        cite.add(url_b)
        bot.reply_to(message, "Выберите кнопку", reply_markup=cite)

    elif message.text == "🎮 Каталог":
        catalog = types.InlineKeyboardMarkup(row_width=1)
        card = types.InlineKeyboardButton(text="🎲 Название игры", callback_data="name")
        all_games = types.InlineKeyboardButton(text="🤖 Все игры", callback_data="all_games")
        catalog.add(card)
        catalog.add(all_games)
        bot.reply_to(message, "Нажмите на кнопку", reply_markup=catalog)

    elif message.text == "🛒 Корзина":
        connect = sqlite3.connect('memes.db')
        cursor = connect.cursor()
        games = cursor.execute("SELECT*FROM basket INNER JOIN game on basket.id_game = game.id_game WHERE id_customer=:id_customer ", {'id_customer': message.chat.id}).fetchall()
        connect.commit()
        connect.close()
        if games:
            for game in games:
                message_text = [
                    f"Название игры: {game[4]}",
                    f"Ограничение по возрасту: {game[5]}",
                    f"Жанр: {game_genre(game[2])}",
                    f"Цена игры: {game[6]} $"
                ]
                bot.send_message(message.chat.id, "\n".join(message_text))
        else:
            bot.send_message(message.chat.id, "Корзина пуста")
    else:
        bot.reply_to(message, message.text, reply_markup=markup_menu)



@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'contact':
            bot.send_message(call.message.chat.id, 'Наш номер телефона: +375(44)-580-25-06 ☎')
        if call.data == 'name':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Напишите название игры 🎲')
            bot.register_next_step_handler(call.message, process_game_name_step)
        if call.data.startswith("add_game_to_basket_"):
            game_id = call.data.replace("add_game_to_basket_", "")
            connect = sqlite3.connect('memes.db')
            cursor = connect.cursor()
            cursor.execute("INSERT INTO basket (id_customer, id_game) VALUES (:id_customer,:id_game)",
                           {"id_customer": call.from_user.id, "id_game": game_id})
            connect.commit()
            connect.close()
            bot.send_message(call.message.chat.id, "Добавлено")
        if call.data.startswith("show_game_info_"):
            game_id = call.data.replace("show_game_info_", "")
            connect = sqlite3.connect('memes.db')
            cursor = connect.cursor()
            game = cursor.execute("SELECT * from game WHERE id_game = :0", {'0': game_id}).fetchone()
            game_info_message(call.message, game, "msg_edit")
            connect.close()
        if call.data == "all_games":
            connect = sqlite3.connect('memes.db')
            cursor = connect.cursor()
            all_games = cursor.execute("SELECT * from game").fetchall()
            keyboard = types.InlineKeyboardMarkup()
            for game in all_games:
                game_btn = types.InlineKeyboardButton(game[1], callback_data="show_game_info_" + str(game[0]))
                keyboard.add(game_btn)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🤖 Все игры!', reply_markup=keyboard)
            connect.close()


def process_game_name_step(message):
    game_name = message.text
    connect = sqlite3.connect('memes.db')
    cursor = connect.cursor()
    search_result = cursor.execute("SELECT * from game").fetchall()
    for game in search_result:
        if fuzz.WRatio(game[1], game_name) >= 85:
            game_info_message(message, game)
            break
    else:
        bot.send_message(message.chat.id, "К сожалею, такой игры не нашлось 😔")
    connect.close()


def game_info_message(message, game, msg_type="answer"):
    keyboard = types.InlineKeyboardMarkup()
    buy_game_btn = types.InlineKeyboardButton("Добавить в корзину", callback_data="add_game_to_basket_" + str(game[0]))
    keyboard.add(buy_game_btn)
    message_text = [
        f"Название игры: {game[1]}",
        f"Ограничение по возрасту: {game[2]}",
        f"Жанр: {game_genre(game[0])}",
        f"Цена игры: {game[3]}$"
    ]
    if msg_type == "answer":
        bot.send_message(message.chat.id, '\n'.join(message_text), reply_markup=keyboard)
    elif msg_type == "msg_edit":
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='\n'.join(message_text), reply_markup=keyboard)


def game_genre(game_id):
    game_genres_list = []
    connect = sqlite3.connect('memes.db')
    cursor = connect.cursor()
    game_genres = cursor.execute("SELECT * FROM game_zhanr WHERE id_game = :0", {'0': game_id}).fetchall()
    for game in game_genres:
        zhanr = cursor.execute("SELECT * FROM zhanr WHERE id_zhanr = :0", {'0': game[1]}).fetchone()
        game_genres_list.append(zhanr[1])
    connect.close()
    return ', '.join(game_genres_list)

def add_game_to_basket_message(message, game_id):
    print(game_id)

bot.polling(none_stop=True)
