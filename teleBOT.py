import con_to_postgres
from con_to_postgres import connection  ## FROM YOUR conn DB
from config import TOKEN
import telebot
from telebot import types

bot = telebot.TeleBot(token=TOKEN)

cursor = connection.cursor()



@bot.message_handler(commands=["start"])
def start_commands(message):
    # bot.send_message(message.chat.id, "Привет!", reply_markup=markup)
    get_all_prod = types.KeyboardButton(text="/allprods")
    get_prod_by_id = types.KeyboardButton(text="/prodbyid")
    brand_name = types.KeyboardButton(text="/brandbyname")
    category_name = types.KeyboardButton(text="/categbyname")
    del_by_id = types.KeyboardButton(text="/delbyID")
    update_info = types.KeyboardButton(text="/update")
    insert_info = types.KeyboardButton(text="/insert")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(get_all_prod, get_prod_by_id, brand_name, category_name, del_by_id, update_info, insert_info)
    bot.send_message(message.chat.id, "Привет!", reply_markup=markup)

@bot.message_handler(commands=["allprods"])
def get_allprods(message):
    products = con_to_postgres.get_all_product()
    mess = ''
    for prod in products:
        mess += str(prod[0]) + ':' + prod[1] + '\n'
    bot.send_message(message.chat.id, mess)

@bot.message_handler(commands=["prodbyid"])
def get_prod_id(message):
    # product = con_to_postgres.get_product_id(prod_id= message.chat.text)
    # bot.send_message(message.chat.id, str(product))

    msg = bot.send_message(message.chat.id, 'Введите ID продукта')
    bot.register_next_step_handler(msg, process_product_by_id_step)

def process_product_by_id_step(message):
    product = con_to_postgres.get_product_id(prod_id=message.text)
    msg = bot.send_message(message.chat.id, str(product))

@bot.message_handler(commands=["brandbyname"])
def get_brand_name(message):
    brand = con_to_postgres.input_brand()
    msg = bot.send_message(message.chat.id, "Введите брэнд")
    i = ''
    if brand:
        for prod in brand:
            i += f'{prod[0]}\n'
        bot.send_message(message.chat.id, i)
    

    bot.register_next_step_handler(msg, process_brand)

def process_brand(message):
    brand = con_to_postgres.get_brand(brand_name=message.text)
    if brand:
        response = "Результат поиска:\n"
        for prod in brand:
            response += f"Название: {prod[0]}, Цена: {prod[1]}, Категория: {prod[2]}, Брэнд: {prod[3]} \n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Бренд не найден.")
    # msg = bot.send_message(message.chat.id, str(brand))

@bot.message_handler(commands=["categbyname"])
def get_categ_name(message):
    category = con_to_postgres.input_category()
    msg = bot.send_message(message.chat.id, "Введите категорию")
    for i in category:
        bot.send_message(message.chat.id, i)
    bot.register_next_step_handler(msg, process_category)

def process_category(message):
    category = con_to_postgres.get_category(category_name=message.text)
    if category:
        response = "Результаты поиска:\n"
        for cat in category:
            response += f"{cat[0]}, {cat[1]}, {cat[2]}, {cat[3]}\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Категория не найдена.")


@bot.message_handler(commands=["delbyID"])
def del_by_id(message):
    msg = bot.send_message(message.chat.id, "Введите ID для удаления")
    bot.register_next_step_handler(msg, process_del_id)

def process_del_id(message):
    try:
        del_id = int(message.text)
        query = """SELECT * FROM product WHERE id = {};"""
        cursor.execute(query=query.format(del_id))
        row = cursor.fetchone()
        bot.send_message(message.chat.id, "Будет удалена следующая запись: " + str(row))
        msg = bot.send_message(message.chat.id, "Вы уверены что хотите удалить данную запись? Введите только Yes или No: ")
        bot.register_next_step_handler(msg, process_del_confirm, del_id)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели некорректный ID. Введите число.")
        
def process_del_confirm(message, del_id):
    del_confirm = message.text.lower()
    if del_confirm == "yes":
        query = """DELETE FROM product WHERE id = {};"""
        cursor.execute(query=query.format(del_id))
        # connection.commit()
        bot.send_message(message.chat.id, "Товар удален.")
    elif del_confirm == "no":
        bot.send_message(message.chat.id, "Удаление отменено.")
    else:
        msg = bot.send_message(message.chat.id, "Введите только Yes или No: ")
        bot.register_next_step_handler(msg, process_del_confirm, del_id)


@bot.message_handler(commands=["update"])
def update_info(message):
    msg = bot.send_message(message.chat.id, "Введите ID записи, которую хотите обновить")
    bot.register_next_step_handler(msg, process_update_id)

def process_update_id(message):
    try:
        product_id = int(message.text)
        msg = bot.send_message(message.chat.id, "Введите новые данные для обновления")
        bot.register_next_step_handler(msg, lambda m: process_update_data(m, product_id))
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID. Пожалуйста, введите целое число")

def process_update_data(message, product_id):
    try:
        inp_name = message.text
        inp_price = bot.send_message(message.chat.id, "Введите цену продукта:")
        bot.register_next_step_handler(inp_price, lambda m: process_update_price(m, product_id, inp_name))
    except ValueError:
        bot.send_message(message.chat.id, "Некорректные данные. Пожалуйста, введите корректные значения")

def process_update_price(message, product_id, inp_name):
    try:
        inp_price = int(message.text)
        inp_description = bot.send_message(message.chat.id, "Введите описание продукта:")
        bot.register_next_step_handler(inp_description, lambda m: process_update_description(m, product_id, inp_name, inp_price))
    except ValueError:
        bot.send_message(message.chat.id, "Некорректные данные. Пожалуйста, введите корректные значения")

def process_update_description(message, product_id, inp_name, inp_price):
    try:
        inp_description = message.text
        inp_category = bot.send_message(message.chat.id, "Введите категорию:\n1: Смартфоны\n2: Планшеты\n3: Смарт часы\n")
        bot.register_next_step_handler(inp_category, lambda m: process_update_category(m, product_id, inp_name, inp_price, inp_description))
    except ValueError:
        bot.send_message(message.chat.id, "Некорректные данные. Пожалуйста, введите корректные значения")

def process_update_category(message, product_id, inp_name, inp_price, inp_description):
    try:
        inp_category = int(message.text)
        if inp_category not in [1, 2, 3]:
            raise ValueError
        inp_brand = bot.send_message(message.chat.id, "Введите бренд продукта:\n1: Apple\n2: Xiaomi\n3: Samsung\n")
        bot.register_next_step_handler(inp_brand, lambda m: process_update_brand(m, product_id, inp_name, inp_price, inp_description, inp_category))
    except ValueError:
        bot.send_message(message.chat.id, "Некорректные данные. Пожалуйста, введите корректные значения")

def process_update_brand(message, product_id, inp_name, inp_price, inp_description, inp_category):
    try:
        inp_brand = int(message.text)
        if inp_brand not in [1, 2, 3]:
            raise ValueError
        con_to_postgres.update_prod(product_id, inp_name, inp_price, inp_description, inp_category, inp_brand)
        bot.send_message(message.chat.id, "Запись успешно обновлена")
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка")


@bot.message_handler(commands=["insert"])
def insert_info_handler(message):
    msg = bot.send_message(message.chat.id, "Введите название продукта:")
    bot.register_next_step_handler(msg, get_product_name)

def get_product_name(message):
    product_name = message.text
    msg = bot.send_message(message.chat.id, "Введите цену продукта:")
    bot.register_next_step_handler(msg, get_product_price, product_name)

def get_product_price(message, product_name):
    product_price = message.text
    msg = bot.send_message(message.chat.id, "Введите описание продукта:")
    bot.register_next_step_handler(msg, get_product_description, product_name, product_price)

def get_product_description(message, product_name, product_price):
    product_description = message.text
    msg = bot.send_message(message.chat.id, "Введите категорию продукта:\n1: Смартфоны\n2: Планшеты\n3: Смарт часы\n")
    bot.register_next_step_handler(msg, get_product_category, product_name, product_price, product_description)

def get_product_category(message, product_name, product_price, product_description):
    product_category = message.text
    msg = bot.send_message(message.chat.id, "Введите брэнд продукта:\n1: Apple\n2: Xiaomi\n3: Samsung\n")
    bot.register_next_step_handler(msg, get_product_brand, product_name, product_price, product_description, product_category)

def get_product_brand(message, product_name, product_price, product_description, product_category):
    product_brand = message.text
    con_to_postgres.insert_info(product_name, product_price, product_description, product_category, product_brand)
    bot.send_message(message.chat.id, f"Вы добавили запись: {product_name}, {product_price}, {product_description}, {product_category}, {product_brand}")


if __name__ == '__main__':
    print("Start bot ...")
    bot.infinity_polling()
