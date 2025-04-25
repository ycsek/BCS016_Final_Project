"""
Author: Jason
E-mail: D23090120503@cityu.edu.mo
LastEditTime: 2025-04-25 13:34:08
"""

import pymysql.cursors

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "library_db",
    "cursorclass": pymysql.cursors.DictCursor,
}
