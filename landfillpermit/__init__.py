import os
import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# Set root user info for web application
root_user = ""
root_password = ""
if os.getenv('ROOT_USER'):
    root_user = os.getenv('ROOT_USER')

if os.getenv('ROOT_PASSWORD'):
    root_password = bcrypt.hashpw(str.encode(os.getenv('ROOT_PASSWORD')), bcrypt.gensalt())

# Setup DB connection
db_url = os.getenv('DB_TYPE')
db_path = os.getenv('DB_PATH')
db_name = os.getenv('DB_NAME')
if not db_url:
    raise ValueError('please set environmental variable DB_TYPE to type of DB to be used. Ex. "sqlite", "mysql", etc')
if not db_path:
    raise ValueError('please set environmental variable DB_PATH to the database path. Ex. local sqlite db "//data.db" or remote "db.example.com"')
if not db_name:
    raise ValueError('please set environmental variable DB_NAME to the name of the database to use')
if os.getenv('DB_DRIVER'):
    db_url = db_url + "+" + os.getenv('DB_DRIVER')
db_url += "://"

if os.getenv('DB_USER'):
    db_url += os.getenv('DB_USER')
    if len(os.getenv('DB_PASS')) > 0:
        db_url += ":" + os.getenv('DB_PASS')
    db_url += "@"

db_url += db_path
db_url += "/" + db_name

tls_cert = os.getenv('DB_TLS_CERT')
if tls_cert:
    db_url += "?ssl_ca=" + os.path.join(os.getcwd(), 'landfillpermit/', tls_cert)
    print(db_url)

engine = create_engine(db_url)


#Setup mailgun info
mg_domain = os.getenv('MG_DOMAIN')
if not mg_domain:
    raise ValueError('please set environmental variable MG_DOMAIN to your Mailgun domain')

mg_api_key = os.getenv('MG_API_KEY')
if not mg_api_key:
    raise ValueError('please set environmental variable MG_API_KEY to your Mailgun private API key')