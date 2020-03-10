import dj_database_url
import psycopg2
import os
from config import DATABASELINK

db_info = dj_database_url.config(default=DATABASELINK)
connection = psycopg2.connect(database=db_info.get('NAME'), user=db_info.get('USER'), password=db_info.get('PASSWORD'),
                              host=db_info.get('HOST'), port=db_info.get('PORT'))
cursor = connection.cursor()
