from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

def get_fora_database():
    fora_db = MongoClient(os.getenv('MONGO_URI'))['Fora']
    return fora_db


def blacklist_user_add(user_id: int, author_id: int, reason: str):
    """
    Adds a user to the blacklist
    """
    get_fora_database()["blacklist"].insert_one({
        "_id": user_id, 
        "time": str(datetime.date.today()),
        "author_id": author_id,
        "reason": reason
    })


def blacklist_user_remove(user_id: int):
    """
    Removes a user from the blacklist
    """
    get_fora_database()["blacklist"].delete_one({"_id": user_id})


def blacklist_user_get(user_id: int):
    """
    Returns a user from the blacklist
    """
    return get_fora_database()["blacklist"].find_one({"_id": user_id})
