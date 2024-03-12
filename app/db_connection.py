import os

IP = os.getenv("DB_HOST")
# CONNECTION_STRING = f"postgresql+psycopg2://admin:root@{IP}:5432/db"
CONNECTION_STRING = f"postgresql+psycopg2://admin:root@127.0.0.1:5432/db"