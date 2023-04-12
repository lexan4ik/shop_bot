from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
import sqlite3 as sl
import json

TOKEN = '5920303573:AAFgWZZfqdUclJkDWXHoXWnAxIMGmsRaYZA'

bot = telebot.TeleBot(TOKEN)

#Сохранение файлов
def save_setting(name,data):
    with open(f"{name}.json", "w") as f:
        json.dump(data, f)
#Загрузка файлов
def load_setting(name):
    try:
        with open(f"{name}.json", "r") as f:
            load_sett = json.load(f)
            print(f'Файл {name} инициализирован')
        return load_sett

    except:
        print(f'Файл {name} не найден!')
        pass

def pythonify(json_data):

    correctedDict = {}

    for key, value in json_data.items():
        if isinstance(key, list):
            value = [pythonify(item) if isinstance(item, dict) else item for item in value]
        try:
            key = int(key)
        except Exception as ex:
            pass
        correctedDict[key] = value

    return correctedDict

category = ['Продукты','Одежда','Обувь','Другое']

message_id = {}

states = {}

states_order = {}

message_edit = {}
#Пробуем подгрузить корзину или или создать пустой словарь
try:
    cart = pythonify(load_setting('cart').copy())
    print('Файл с корзиной загружен')
except:
    cart = {}
    print('Не удалось загрузить файл с корзиной')
#Пробуем подгрузить заказы или создать пустой словарь
try:
    order = load_setting('order').copy()
    print('Файл с заказами загружен')
except:
    order = {}
    print('Не удалось загрузить файл с заказами')
#Пробуем подгрузить товары или создать пустой словарь
try:
    products = load_setting('products').copy()
    print('Файл с продуктами загружен')
except:
    products = {}
    print('Не удалось загрузить файл с продуктами')
#Пробуем подгрузить Админов или создать пустой словарь
try:
    admins = pythonify(load_setting('admins').copy())
    print('Файл с Админами загружен')
except:
    admins = {665909535: {'rights': True}, 5385544355: {'rights': True}}
    print('Не удалось загрузить файл с Админами')

admin_chat = -1001670297855

con = sl.connect('User_DB.db', check_same_thread=False)



with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS USER (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        tg_id NCHAR,
        first_name CHARACTER,
        last_name CHARACTER,
        address VARCHAR,
        phone CHARACTER,
        UNIQUE(tg_id),
        UNIQUE(phone)
        );""")
    con.execute("""CREATE TABLE IF NOT EXISTS USER_ORDER (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        prod_id INT,
        tg_id NCHAR,
        name_product VARCHAR,
        price_product INT,
        count INT,
        status NCHAR DEFAULT 'Ожидает обработки',
        contact_info TEXT,
        payment VARCHAR
        );""")
