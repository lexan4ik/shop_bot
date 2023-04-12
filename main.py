import telebot.apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
from telebot import types
import telebot
from other import TOKEN,message_id,message_edit,products,\
    admin_chat,admins,states,save_setting,cart,order,states_order
from functions_db import BotDB
from functions_main import *

bot = telebot.TeleBot(TOKEN)

#Отлов фото
@bot.message_handler(content_types=['photo'])
def photo(message):
    user_id = message.chat.id
    if states[user_id]['photo'] is True:
        bot.send_message(user_id,'Вы успешно добавили товар!')
        products[states[user_id]['prod_id']][user_id]['photo'] = message.photo[-1].file_id
        states[user_id]['photo'] = False
        save_setting('products', products)

#Отлов старта
@bot.message_handler(commands=['start'])
def start(message):
    global products
    user_id = message.chat.id
    if message.text == '/start':
        bot.send_message(user_id,'Добро пожаловать в интернет-магазин!',reply_markup=menu_keyb())
        message_edit[user_id] = {}


#Отлов админ-меню
@bot.message_handler(commands=['admin','admins','Admins','Admin'])
def start_admin(message):
    user_id = message.chat.id
    check_user(user_id)
    if user_id not in message_id:
        message_id[user_id] = {}

#Отлов сообщнеий
@bot.message_handler(content_types=['text'])
def spuff_message(message):
    user_id = message.chat.id
    text = message.text
    if user_id not in cart:
        cart[user_id] = {}
    if user_id not in message_id:
        message_id[user_id] = {}

    #Обработка меню
    if text.lower() == 'товары':
        bot.delete_message(user_id,message.id)
        bot.send_message(user_id,'Выберите категорию товара:',reply_markup=category_list())
        if 'cart' in message_id[user_id]:
            del message_id[user_id]['cart']
    elif text.lower() == 'корзина':
        msg = bot.send_message(user_id,'Ваша корзина:',reply_markup=carts_keyb(user_id))
        message_id[user_id]['cart'] = msg.id
        print(cart)
    elif text.lower() == 'заказы':
        my_orders(user_id)
    elif text.lower() == 'помощь':
        print('помощь')

    #Состояния для добавление товара:
    if user_id not in states:
        pass
    elif states[user_id]['name'] is True:
        if message.text.lower() == 'отмена':
            del products[states[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states[user_id]['name'] = False
        else:
            mess = ''
            for i in category:
                mess += f' {i} '
            bot.send_message(message.chat.id, f'Отправте категорию из перечисленых:\n{mess}')
            products[states[user_id]['prod_id']][user_id]['name'] = message.text.lower()
            states[user_id]['name'] = False
            create_product(message,states[user_id]['prod_id'])

    elif states[user_id]['category'] is True:
        if message.text.lower() == 'отмена':
            del products[states[user_id]['prod_id']]
            bot.send_message(user_id, 'Вы отменили добавление товара!')
            states[user_id]['category'] = False
        else:
            for i in category:
                if i.lower() != text.lower():
                    states[user_id]['name'] = False
                    create_product(message, states[user_id]['prod_id'])
                elif i.lower() == text.lower():
                    bot.send_message(message.chat.id, 'Отправте цену товара:')
                    products[states[user_id]['prod_id']][user_id]['category'] = message.text.lower()
                    states[user_id]['category'] = False
                    create_product(message, states[user_id]['prod_id'])
                    break

    elif states[user_id]['price'] is True:
        if message.text.lower() == 'отмена':
            del products[states[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states[user_id]['price'] = False
        else:
            bot.send_message(message.chat.id, 'Отправте описание товара:')
            products[states[user_id]['prod_id']][user_id]['price'] = message.text
            states[user_id]['price'] = False
            create_product(message, states[user_id]['prod_id'])

    elif states[user_id]['desc'] is True:
        if message.text.lower() == 'отмена':
            del products[states[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states[user_id]['desc'] = False
        else:
            bot.send_message(message.chat.id, 'Отправте фото товара:')
            products[states[user_id]['prod_id']][user_id]['desc'] = message.text.lower()
            states[user_id]['desc'] = False
            create_product(message, states[user_id]['prod_id'])

    elif states[user_id]['photo'] is True and message.text:
        if message.text.lower() == 'отмена':
            del products[states[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states[user_id]['photo'] = False
        else:
            bot.send_message(user_id,'Вы отправили не фотографию, попробуйте еще раз')

    #Обработка состояний для добавления заказа
    if user_id not in states_order:
        pass
    elif states_order[user_id]['address'] is True:
        if message.text.lower() == 'отмена':
            del order[states_order[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states_order[user_id]['address'] = False
        else:
            order[states_order[user_id]['prod_id']][user_id]['address'] = message.text
            states_order[user_id]['address'] = False
            bot.send_message(user_id,'Введите Вашу фамилию')
            confirm_order(message, states_order[user_id]['prod_id'])

    elif states_order[user_id]['last_name'] is True:
        if message.text.lower() == 'отмена':
            del order[states_order[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states_order[user_id]['last_name'] = False
        else:
            order[states_order[user_id]['prod_id']][user_id]['last_name'] = message.text
            states_order[user_id]['last_name'] = False
            bot.send_message(user_id,'Введите Ваше имя')
            confirm_order(message, states_order[user_id]['prod_id'])

    elif states_order[user_id]['first_name'] is True:
        if message.text.lower() == 'отмена':
            del order[states_order[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states_order[user_id]['first_name'] = False
        else:
            order[states_order[user_id]['prod_id']][user_id]['first_name'] = message.text
            states_order[user_id]['first_name'] = False
            bot.send_message(user_id,'Введите Ваше отчество')
            confirm_order(message, states_order[user_id]['prod_id'])

    elif states_order[user_id]['middle_name'] is True:
        if message.text.lower() == 'отмена':
            del order[states_order[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states_order[user_id]['middle_name'] = False
        else:
            order[states_order[user_id]['prod_id']][user_id]['middle_name'] = message.text
            states_order[user_id]['middle_name'] = False
            bot.send_message(user_id,'Введите номер телефона в формате: 375xxxxxxxxx')
            confirm_order(message, states_order[user_id]['prod_id'])

    elif states_order[user_id]['phone'] is True:
        if message.text.lower() == 'отмена':
            del order[states_order[user_id]['prod_id']]
            bot.send_message(user_id,'Вы отменили добавление товара!')
            states_order[user_id]['phone'] = False
        else:
            if message.text.isdigit() is True and len(message.text) == 12:
                order[states_order[user_id]['prod_id']][user_id]['phone'] = message.text
                order[states_order[user_id]['prod_id']][user_id]['items'] = [cart[user_id]]
                order[states_order[user_id]['prod_id']][user_id]['status'] = 'Ожидает обработки'
                bot.send_message(user_id, 'Вы успешно оформили заказ!\n Ожидайте его дальнейшей обработки!')
                states_order[user_id]['phone'] = False
                save_setting('order', order)
                send_order(user_id,states_order[user_id]['prod_id'])
            else:
                bot.send_message(user_id, 'Введите номер телефона в формате: 375xxxxxxxxx')
                states_order[user_id]['middle_name'] = False
                confirm_order(message, states_order[user_id]['prod_id'])
        print(order)



    if 'addadmin' in message_id[user_id]:
        if message.text.lower() == 'отмена':
            del message_id[user_id]['addadmin']
            bot.send_message(user_id,'Вы отменили добавление Администратора/Продавца')
        elif message_id[user_id]['addadmin'] is True:
            new_admin(message)
            message_id[user_id]['addadmin'] = False
            save_setting('admins', admins)

@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    bot.answer_callback_query(callback_query_id=call.id,)
    id = call.message.chat.id
    flag = call.data[0:8]
    data = call.data[8:]

    if flag == 'order000':
        order[states_order[id]['prod_id']][id]['status'] = 'В обработке'
    if flag == 'order001':
        order[states_order[id][data]][id]['status'] = 'Завершен'

    #Выдача клавиатуры с выбором способа доставки
    if flag == 'addorder':
        bot.send_message(id,'Выберите способ доставки:',reply_markup=dilivery())
    #Оформление заказа по почте
    if flag == 'mailpick':
        max_id = int(max(order.keys())) if order else 10000
        order[max_id + 1] = {id: {'address': '', 'last_name': '', 'first_name': '', 'middle_name': '', 'phone': ''}}
        bot.delete_message(id, call.message.id)
        msg = bot.send_message(id, 'Вы так же можете отменить добавление написав: "отмена"')
        states_order[id] = {}
        states_order[id]['prod_id'] = max_id + 1
        bot.send_message(id,'Введите адресс доставки:\n Область,город,ул,дом')
        confirm_order(msg, max_id+1)

    #Получаем список всех Администраторов или Продавцов
    if flag == 'listadm0':
        bot.send_message(id,'Вот все Администраторы:',reply_markup=check_admins('admin'))
    if flag == 'listsell':
        bot.send_message(id, 'Вот все Продавцы:', reply_markup=check_admins('seller'))
    #Изменение Прав Администратора или Продавца
    if flag == 'adm_list':
        flag_adm = InlineKeyboardMarkup()
        flag_adm.add(InlineKeyboardButton('Пользователь',callback_data=f'addusers{data}'),
                     InlineKeyboardButton('Отмена',callback_data='menu'),
                     InlineKeyboardButton('Продавец',callback_data=f'addseler{data}'))
        bot.send_message(id,f'Изменить права для Администратора {data}',reply_markup=flag_adm)
    if flag == 'sel_list':
        flag_adm = InlineKeyboardMarkup()
        flag_adm.add(InlineKeyboardButton('Пользователь', callback_data=f'addusers{data}'),
                     InlineKeyboardButton('Отмена', callback_data='menu'),
                     InlineKeyboardButton('Администратор', callback_data=f'addadmin{data}'))
        bot.send_message(id, f'Изменить права для Продавца {data}', reply_markup=flag_adm)
    #Изменение прав на Пользователя
    if flag == 'addusers':
        admins[int(data)]['rights'] = None
        bot.send_message(id,f'{int(data)} добавлен как Пользователь')
        save_setting('admins', admins)
    #Добавление/изменение прав на Администратора
    if flag == 'addadmin':
        admins[int(data)]['rights'] = True
        bot.send_message(id,f'{int(data)} добавлен как Администратор')
        save_setting('admins', admins)
    #Добавление/изменение прав на Продавца
    if flag == 'addseler':
        admins[int(data)]['rights'] = False
        bot.send_message(id,f'{int(data)} добавлен как Продавец')
        save_setting('admins', admins)
    #Добавление Администратора
    if flag == 'newadmin':
        message_id[id]['addadmin'] = True
        bot.send_message(id, 'Вы так же можете отменить добавление написав: "отмена"')
        bot.send_message(id,'Перешлите текстовое сообщение от пользователя.')


    #Добавление товара в бота
    if flag == 'add_prod':
        max_id = int(max(products.keys())) if products else 10000
        products[str(max_id+1)] = {id: {'name': '','category': '','price': '','desc': '','photo': ''}}
        msg = bot.send_message(id,'Вы так же можете отменить добавление написав: "отмена"')
        states[id] = {}
        states[id]['prod_id'] = str(max_id + 1)
        bot.send_message(id, 'Отправте имя товара:')
        create_product(msg,str(max_id+1))
    #Выдача карточек с товаром
    if flag == 'products':
        category_search(id,data)

    #Добавление в корзину
    if flag == "add_cart":
        from_id = products[data].keys()
        from_id = list(from_id)[0]
        if data not in cart[id]:
            cart[id][data] = products[data]
            if 'count' not in cart[id][data][from_id]:
                cart[id][data][from_id]['count'] = 1
                save_setting('cart', cart)
                add_count_cart(id, data)
        else:
            add_count_cart(id, data)
            bot.send_message(id,'Товар уже находиться у вас в корзине!')
        print(cart)
    #Уменьшение кол-ва в корзине
    if flag == 'mincount':
        from_id = products[data].keys()
        from_id = list(from_id)[0]
        if int(cart[id][data][from_id]['count']) <= 1:
            del cart[id][data]
            bot.delete_message(id,call.message.id)
            bot.send_message(id,'Товар удален из вашей корзины!')
            print(cart)
        else:
            cart[id][data][from_id]['count'] -= 1
            if 'cart' in message_id[id]:
                bot.edit_message_text('Ваша корзина',id,message_id[id]['cart'],reply_markup=carts_keyb(id))
            else:
                add_count_cart(id,data)
        save_setting('cart', cart)

    #Увеличение кол-ва в корзине
    if flag == 'addcount':
        from_id = products[data].keys()
        from_id = list(from_id)[0]
        cart[id][data][from_id]['count'] +=1
        if 'cart' in message_id[id]:
            bot.edit_message_text('Ваша корзина',id,message_id[id]['cart'],reply_markup=carts_keyb(id))
        else:
            add_count_cart(id, data)
        save_setting('cart', cart)

    #Стартовое меню
    if flag == "menu":
        bot.send_message(id, 'Добро пожаловать в интернет-магазин!', reply_markup=menu_keyb())


if __name__ == "__main__":
    print("Bot started")
    bot.infinity_polling()
