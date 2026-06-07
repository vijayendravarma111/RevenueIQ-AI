from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = quote_plus(os.getenv("MYSQL_PASSWORD"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

def get_engine():

    connection_string = (
        f"mysql+pymysql://"
        f"{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}"
        f"/{MYSQL_DATABASE}"
    )

    return create_engine(connection_string)

if __name__ == "__main__":

    engine = get_engine()

    with engine.connect():
        print("Database Connected Successfully")
        
    print("HOST =", MYSQL_HOST)
    print("PORT =", MYSQL_PORT)
    print("USER =", MYSQL_USER)
    print("DB =", MYSQL_DATABASE)