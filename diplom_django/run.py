import os
os.system("python3 manage.py db_filling")
os.system("python3 manage.py runserver 0.0.0.0:8000")