from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup,KeyboardButton
from telebot.types import InputMediaPhoto
from other import message_id,bot,category,admins,states,cart,states_order,states,order,admin_chat
from main import BotDB,products
from functions_db import BotDB
import telebot
import json

BotDB = BotDB('User_DB.db')

#Обработка заказов из Админ чата
def send_order(user_id,item):
    keyboard = InlineKeyboardMarkup()
    total_sum = 0
    for i in item['items']:
        for a, b in i.items():
            print(a,b)
            for k, j in b.items():
                pass
            total_sum += int(j['price']) * int(j['count'])
            keyboard.add(InlineKeyboardButton(
                text=f'{j["name"]}: {j["price"]}byn * {j["count"]}шт == {int(j["price"]) * int(j["count"])}byn',
                callback_data='faddf'))
            print(j)
        keyboard.add(InlineKeyboardButton(text=f"Итоговая сумма: {total_sum} byn", callback_data='suuum'))
        keyboard.add(InlineKeyboardButton(text=f"Статус заказа: {item['status']}", callback_data='status'))
        keyboard.add(InlineKeyboardButton(text=f"Обработка",callback_data=f'order000{item}'),InlineKeyboardButton('Завершен',callback_data=f'order001{item}'))
    bot.send_message(admin_chat, f'Пришел новый заказ от пользователя: {user_id}!' ,reply_markup=keyboard)


#Выдача стартового меню
def menu_keyb():
    menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    product = KeyboardButton('Товары')
    cart = KeyboardButton('Корзина')
    order = KeyboardButton('Заказы')
    me_help = KeyboardButton('Помощь')
    menu_keyboard.row(product,cart)
    menu_keyboard.row(order,me_help)
    return menu_keyboard

#Добавление нового Администратора
def new_admin(message):
    if message.chat.id in admins and admins[message.chat.id]['rights'] is True:
        print(message)
        try:
            admin_keyb = InlineKeyboardMarkup()
            forward_id = message.forward_from.id
            admins[forward_id] = {}
            admin_keyb.add(InlineKeyboardButton('Администратор', callback_data=f'addadmin{forward_id}'),
                           InlineKeyboardButton('Продавец', callback_data=f'addseler{forward_id}'))
            bot.send_message(message.chat.id, "Укажите уровень прав", reply_markup=admin_keyb)
        except:
            bot.send_message(message.chat.id,'Что-то пошло не так!')

#Панель Администратора
def admin_panel():
    admin_keyboard = InlineKeyboardMarkup()
    admin_keyboard.add(InlineKeyboardButton('Список Администраторов',callback_data='listadm0'))
    admin_keyboard.add(InlineKeyboardButton('Список Продавцов',callback_data='listsell'))
    admin_keyboard.add(InlineKeyboardButton('Статистика',callback_data='statprod'))
    admin_keyboard.add(InlineKeyboardButton('Добавить товар',callback_data='add_prod'))
    admin_keyboard.add(InlineKeyboardButton('Добавить Администратора',callback_data='newadmin'))
    return admin_keyboard

def check_admins(flag=''):
    admin_keyb = InlineKeyboardMarkup()
    for a,b in admins.items():
        if b['rights'] is True and flag == 'admin':
                admin_keyb.add(InlineKeyboardButton(f'Админ {a}',callback_data=f'adm_list{a}'))
        if b['rights'] is False and flag == 'seller':
                admin_keyb.add(InlineKeyboardButton(f'Продавец {a}',callback_data=f'sel_list{a}'))
    return admin_keyb

#Проверка пользователя на права и выдача соответствующего меню
def check_user(user_id):
    if user_id not in admins:
        bot.send_message(user_id,'Вы обычный пользователь!')
    elif admins[user_id]['rights'] is True:
        bot.send_message(user_id,'Вы Администратор!',reply_markup=admin_panel())
    elif admins[user_id]['rights'] is False:
        bot.send_message(user_id,'Вы Продавец!')

#Для отслеживания состояний при добавлении товара
def create_product(message,prod_id):
    global products
    for a,b in products[prod_id][message.chat.id].items():
        if not b or states[message.chat.id][a] is not False:
            states[message.chat.id][a] = True
            break

#Для отслеживания состояний при оформлении заказа
def confirm_order(message,order_id):
    for a,b in order[int(order_id)][message.chat.id].items():
        print(a)
        if not b or states_order[message.chat.id][a] is not False:
            states_order[message.chat.id][a] = True
            break
#Генерирует клавиатуру по списку продуктов
def category_list():
    category_keyboard = InlineKeyboardMarkup()
    for i in category:
        category_keyboard.add(InlineKeyboardButton(i,callback_data='products'+i))
    category_keyboard.add(InlineKeyboardButton('В меню', callback_data='menu'))
    return category_keyboard

#Выдает карточки продуктов исходя из категории
def category_search(user_id,category):
    for a,b in products.items():
        for k,j in b.items():
            if category.lower() in j['category'].lower():
                text = f"{j['name']}({a})\n\n{j['price']} byn\n\n{j['desc']}"
                photo = j['photo']
                add_cart(user_id, text, photo,a)
#Кнопка "Добавить в корзину" для карточек и дальшейшей выдичи кнопок кол-ва
def add_cart(user_id,text,photo,result_id):
    cart_add = InlineKeyboardMarkup()
    cart_add.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'add_cart{result_id}'))
    msg = bot.send_photo(user_id, photo, caption=text, reply_markup=cart_add)
    message_id[user_id][result_id] = msg.id

#Клавитура кол-ва при добавлении в корзину
def add_count_cart(user_id,result_id):
    add_count = InlineKeyboardMarkup()
    from_id = products[result_id].keys()
    from_id = list(from_id)[0]
    count = cart[user_id][result_id][from_id]['count']
    add_count.add(InlineKeyboardButton('🔽', callback_data=f'mincount{int(result_id)}'),
                  InlineKeyboardButton(count, callback_data=f'sumcount{int(result_id)}'),
                  InlineKeyboardButton('🔼', callback_data=f'addcount{int(result_id)}'))
    bot.edit_message_reply_markup(user_id, message_id[user_id][result_id], reply_markup=add_count)

#Выдача корзины
def carts_keyb(user_id):
    keyboard = InlineKeyboardMarkup()
    total_sum = 0
    for a,b in cart[user_id].items():
        for k,j in b.items():
            total_sum += int(j['price']) * int(j['count'])
            keyboard.add(InlineKeyboardButton(text=f'{j["name"]}: {j["price"]}byn * {j["count"]}шт == {int(j["price"]) * int(j["count"])}byn',
                                              callback_data=f'addcount{int(a)}'))
            keyboard.add(InlineKeyboardButton(text='🔽', callback_data=f'mincount{int(a)}'),
                         InlineKeyboardButton(text='🔼', callback_data=f'addcount{int(a)}'),
                         InlineKeyboardButton(text='❌', callback_data=f'deltprod{int(a)}'))
    keyboard.add(InlineKeyboardButton(text=f"Итоговая сумма: {int(total_sum)} byn",callback_data='suuum'))
    keyboard.add(InlineKeyboardButton(text=f'Оформить заказ?',callback_data='addorder'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'menu'))
    return keyboard

#Клавиатура для выбора доставки товара
def dilivery():
    dilivery_keyb = InlineKeyboardMarkup()
    dilivery_keyb.add(InlineKeyboardButton('Самовывоз',callback_data='mepickup'),InlineKeyboardButton('Почта',callback_data='mailpick'))
    return dilivery_keyb

#Список заказов
def my_orders(user_id):
    for a,b in order.items():
        for k,j in b.items():
            pass
        if int(user_id)== int(k):
            status = j['status']
            bot.send_message(user_id, 'Ваши заказы:', reply_markup=show_order(j['items'], status))
        else:
            pass
#Выдача активных заказов
def show_order(item,status):
    keyboard = InlineKeyboardMarkup()
    total_sum = 0
    print(item)
    for i in item:
        for a,b in i.items():
            for k,j in b.items():
                pass
            total_sum += int(j['price']) * int(j['count'])
            keyboard.add(InlineKeyboardButton(
                text=f'{j["name"]}: {j["price"]}byn * {j["count"]}шт == {int(j["price"]) * int(j["count"])}byn',callback_data='faddf'))
            print(j)
        keyboard.add(InlineKeyboardButton(text=f"Итоговая сумма: {total_sum} byn", callback_data='suuum'))
        keyboard.add(InlineKeyboardButton(text=f"Статус заказа: {status}",callback_data='status'))
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'menu'))
        return keyboard