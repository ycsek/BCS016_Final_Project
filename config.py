
import pymysql.cursors

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "library_db",
    "cursorclass": pymysql.cursors.DictCursor,
}
