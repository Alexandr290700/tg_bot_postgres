import psycopg2
from psycopg2.errors import InvalidTextRepresentation
from datetime import datetime
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(
    dbname = os.getenv("DBNAME"),
    user = os.getenv("USERDB"),
    password = os.getenv("PASSWORD"),
    host = os.getenv('HOST'),
    port = os.getenv("PORT")
)


# print(connection)


cursor = connection.cursor()

def get_all_product():
    query = """
    SELECT * FROM product
    ;
    """
    cursor.execute(query=query)
    all_product = cursor.fetchall()
    for prod in all_product:
        print(prod)
    return all_product
     

def get_product_id(prod_id):
    query = """
        SELECT * FROM product
        WHERE id = %s;
        """
    cursor.execute(query, (prod_id,))
    product = cursor.fetchone()
    if product:
        product_date = product[4]
        formated_date = product_date.strftime("%Y-%m-%d %H:%M:%S")
        p = (f"""ID: {product[0]}\nНазвание: {product[1]}\nЦена: {product[2]}\nОписание: {product[3]}
Дата создания: {product[4]}\nКатегория: {product[5]}\nБрэнд: {product[6]}""")
        return p
    else:
        return None

    
def get_input_id():
    try:
        prod_id = input("Введите ID продукта: ")
        get_product_id(prod_id)
        while get_product_id(prod_id) is None:
            prod_id = input("Продукт с таким ID не найден. Введите другой ID: ")
            get_product_id(prod_id)
        
        return get_product_id(prod_id)
    except InvalidTextRepresentation:
        e = "ОШИБКА! Введите только цифры!"
        return e


def get_brand(brand_name):
    query = """SELECT p.name, p.price, c.name as category, b.name as brand
         FROM product p
         JOIN brand b ON p.brand = b.brand_id
         JOIN category c ON p.category = c.category_id
         WHERE b.name = %s;
         """
    cursor.execute(query, (brand_name,))
    brand = cursor.fetchall()
    return brand

def input_brand():
    query = """SELECT brand.name FROM brand;
            """
    cursor.execute(query=query)
    prod = cursor.fetchall()
    return prod
    # brand_name = input("Введите название бренда: ")
    # get_brand(brand_name)


def get_category(category_name):
    query = """SELECT p.name, p.price, c.name as category, b.name as brand
        FROM product p
        JOIN brand b ON p.brand = b.brand_id
        JOIN category c ON p.category = c.category_id
        WHERE c.name = %s
    ; 
    """
    cursor.execute(query, (category_name, ))
    categ = cursor.fetchall()
    return categ
    # for i in categ:
    #     return i

def input_category():
    query = """SELECT category.name FROM category;
            """
    cursor.execute(query=query)
    category = cursor.fetchall()
    return category
    # category_name = input("Введите категорию: ")
    # get_category(category_name)


def del_prod_by_id(del_id):
    query = """SELECT * FROM product
    WHERE id = {};""" 
    cursor.execute(query=query.format(del_id))
    row = cursor.fetchone()
    print("Будет удалена следующая запись: ")
    print(row)
    del_confirm = input("Вы уверены что хотите удалить данную запись? Введите только Yes или No: ")
    if del_confirm == "Yes":
        query = """DELETE FROM product
        WHERE id = {};
        """
        cursor.execute(query=query.format(del_id))
        connection.commit()
    elif del_confirm == "No":
        return main()
    else:
        print("ОШИБКА! Введите только Yes или No!")
       

def del_prod_id():
    del_id = input("Введите ID для удаления: ")
    del_prod_by_id(del_id)


def insert_info(inp_name, inp_price, inp_description, inp_category, inp_brand):
    query_all = """SELECT product.name FROM product;"""
    # inp_name = input("Введите название продукта: ")
    # inp_price = input("Введите цену продукта: ")
    # inp_description = input("Введите описание: ")
    # inp_category = input("""Введите категорию:\n1: Смартфоны\n2: Планшеты\n3: Смарт часы\n """)
    # inp_brand = input("Введите брэнд продукта:\n 1: Apple\n 2: Xiaomi\n 3: Samsung\n")
    query = """INSERT INTO product (name, price, descriprtion, category, brand)
                VALUES (%s, %s, %s, %s, %s)"""
    # values = (inp_name, inp_price, inp_description, inp_category, inp_brand)
    cursor.execute(query, (inp_name, inp_price, inp_description, inp_category, inp_brand))
    connection.commit()
    # print(f"Вы добавили запись: {inp_name}, {inp_price}, {inp_description}, {inp_category}, {inp_brand}")

def update_prod(product_id, inp_name, inp_price, inp_description, inp_category, inp_brand):
    # inp_name = input("Введите название продукта: ")
    # inp_price = input("Введите цену продукта: ")
    # inp_description = input("Введите описание: ")
    # inp_category = input("""Введите категорию:\n1: Смартфоны\n2: Планшеты\n3: Смарт часы\n """)
    # inp_brand = input("Введите брэнд продукта:\n 1: Apple\n 2: Xiaomi\n 3: Samsung\n")
    query = """UPDATE product
                SET name = %s, price = %s, descriprtion = %s, category = %s, brand = %s
                WHERE id = %s;"""
    # values = (inp_name, inp_price, inp_description, inp_category, inp_brand, product_id)
    cursor.execute(query, (inp_name, inp_price, inp_description, inp_category, inp_brand, product_id))
    # connection.commit()
    print(f"Вы обновили запись: {inp_name}, {inp_price}, {inp_description}, {inp_category}, {inp_brand}")

def get_update():
    product_id = input("Введите ID продукта: ")
    print("Вы измените данную запись: ", get_product_id(product_id))
    update_prod(product_id)

def search_category(name):
    query_cat = """SELECT p.name, p.price, c.name as category, b.name as brand
        FROM product p
        JOIN brand b ON p.brand = b.brand_id
        JOIN category c ON p.category = c.category_id
        WHERE c.name = %s;
        """
    cursor.execute(query_cat, (name, ))
    cat = cursor.fetchall()
    return cat

def search_brand(name):
    query_brand = """SELECT p.name, p.price, c.name as category, b.name as brand
        FROM product p
        JOIN brand b ON p.brand = b.brand_id
        JOIN category c ON p.category = c.category_id
        WHERE b.name LIKE %s;
        """
    cursor.execute(query_brand, (name, ))
    b = cursor.fetchall()
    return b


def search_name(name):
    query_name = """SELECT p.name, p.price, c.name as category, b.name as brand
        FROM product p
        JOIN brand b ON p.brand = b.brand_id
        JOIN category c ON p.category = c.category_id
        WHERE p.name LIKE %s;
        """
    cursor.execute(query_name, (f'%{name}%', ))
    n = cursor.fetchone()
    return n
    
    
def input_search():
    cat = """SELECT category.name FROM category"""
    cursor.execute(query=cat)
    c = cursor.fetchall()
    print(c)
    category = input("Введите категорию: ")
    search_category(category)

    all_brand = """SELECT brand.name FROM brand"""
    cursor.execute(query=all_brand)
    b = cursor.fetchall()
    print(b)
    brand = input("Введите брэнд: ")
    search_brand(brand)

    nam = """SELECT product.name FROM product"""
    cursor.execute(query=nam)
    n = cursor.fetchall()
    print(n)
    name = input("Введите название: ")
    print(search_name(name))


def main():
    while True:
        print("1: Показать все продукты")
        print("2: Показать продукт по ID")
        print("3: Показать бренды по имени")
        print("4: Показать категории по имени")
        print("5: Удалить запись")
        print("6: Добавить запись")
        print("7: Обновить запись в БД")
        print("8: Поиск")
        print("9: Выйти из программы")
        command = input("Введите команду: ")
        if command == "1":
            get_all_product()
        elif command == "2":
            print(get_input_id())
        elif command == "3":
            print(input_brand())
           
        elif command == "4":
            input_category()
        
        elif command == "5":
            del_prod_id()
        elif command == "6":
            insert_info()
        elif command == "7":
            get_update()
        elif command == "8":
            input_search()
        elif command == "9":
            break
        else:
            print("Такой команды нет")
            return main()


        break

if __name__ == '__main__':
    main()
