import mysql.connector

def create_connection():
    # Create a connection to the MySQL database
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='db_benzinai_2024')

    # Create a cursor object
    cursor = cnx.cursor()

    return cnx, cursor