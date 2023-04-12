import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        result = self.cursor.execute("SELECT id FROM user WHERE tg_id = ?", user_id)
        return bool(len(result.fetchall()))

    def search_prod_id(self,data):
        result = self.conn.execute("""SELECT id FROM products WHERE name_product = ? and category = ? and 
        price_product = ? and desc_product = ? and raiting = ? and photo = ? """,data)
        return result.fetchall()

