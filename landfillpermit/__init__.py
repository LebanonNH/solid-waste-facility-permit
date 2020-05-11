import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

db_url = os.getenv('DB_TYPE')
db_path = os.getenv('DB_PATH')
if len(db_url) <= 0:
    raise ValueError('please set environmental variable DB_TYPE to type of DB to be used. Ex. "sqlite", "mysql", etc')
if len(db_path) <= 0:
    raise ValueError('please set environmental variable DB_PATH to the database path. Ex. local sqlite db "//data.db" or remote "db.example.com"')
if len(os.getenv('DB_DRIVER')) > 0:
    db_url = db_url + "+" + os.getenv('DB_DRIVER')
db_url += "://"

if len(os.getenv('DB_USER')) > 0:
    db_url += os.getenv('DB_USER')
    if len(os.getenv('DB_PASS')) > 0:
        db_url += ":" + os.getenv('DB_PASS')
    db_url += "@"

db_url += db_path

engine = create_engine(db_url)
mg_domain = os.getenv('MG_DOMAIN')
mg_api_key = os.getenv('MG_API_KEY')