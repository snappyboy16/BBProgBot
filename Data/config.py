from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')

admins = [
    1
]

operators = [] # Заполнять нельзя
