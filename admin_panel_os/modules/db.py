import pymysql.cursors

class DB:
    def __init__(self):
        self.connection = pymysql.connect(host="host",
                                     user="user",
                                     password='pass',
                                     database='db',
                                     cursorclass=pymysql.cursors.DictCursor)

    def get_customers(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM customers WHERE is_done = %s"
            cursor.execute(sql, (0,))
            result = cursor.fetchall()

            return result

    def get_groups(self, customer_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM groups WHERE customer_id = %s"
            cursor.execute(sql, (customer_id,))
            result = cursor.fetchall()

            return result

    def update_customer(self, cid):
        with self.connection.cursor() as cursor:
            sql = "UPDATE customers SET is_done = TRUE WHERE id = %s;"
            cursor.execute(sql, (cid,))
            self.connection.commit()

