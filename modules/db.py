import pymysql.cursors


def save_database(customer):
    connection = pymysql.connect(host="host",
                                 user="user",
                                 password='pass',
                                 database='db',
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection:
        if customer.company_name is None:
            return False
        with connection.cursor() as cursor:
            sql = "INSERT INTO `customers` (`company_name`, `address`, `tax_number`, `registration_number`, `payment_frequency`, `broker`, `email`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (customer.company_name, customer.address, customer.tax_number, customer.registration_number, customer.payment_frequency, customer.broker, customer.email))
            last_id = cursor.lastrowid
        connection.commit()

        with connection.cursor() as cursor:
            for group in customer.groups:
                cmr_db = ""
                baf_db = ""
                for clause in group.cmr_clauses:
                    if clause[2]:
                        cmr_db += '1'
                    else:
                        cmr_db += '0'
                for clause in group.baf_clauses:
                    if clause[2]:
                        baf_db += '1'
                    else:
                        baf_db += '0'
                sql = "INSERT INTO `groups` (`customer_id`, `number_of_trucks`, `cmr_limit`, `baf_limit`, `cabotage`, `group_number`, `cmr_clauses`, `baf_clauses`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (last_id, group.number_of_trucks, group.cmr_limit, group.baf_limit, group.cabotage, group.group_number, cmr_db, baf_db))
        connection.commit()
        return True
