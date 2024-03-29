import mysql.connector
import psycopg2
import sys

cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='password',
    database='pcbprototype',
    port='3306'
)

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    user='postgres',
    password='password',
    database='pcbprototype'
)

def checkConnection():
    print("host: " + conn.info.host)
    print("name: " + conn.info.dbname)
    print("user: " + conn.info.user)
    x = input("Continue  (o/quit) >>> ")
    if(x != 'o'):
        sys.exit()

# conn = psycopg2.connect(
#     host='135.125.133.20',
#     port='5432',
#     user='postgres',
#     password='LE%gh6Xz5AZ72%',
#     database='pcbprototype'
# )

from hashlib import md5

class MD5:
    def __init__(self, data = "Hello, world!"):
        self.data = data
    def encrypt(self):
        self.data = md5(self.data.encode()).hexdigest()
        return "Crypted: "+self.data
    def decrypt(self, data):
        if md5(data.encode()).hexdigest() == self.data:
            return "Decrypted: "+data
            del self.data
        else:
            return "Error"
