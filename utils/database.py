from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os

load_dotenv()
get_fora_database = MongoClient(os.getenv('MONGO_URI'))['Fora']
blacklist = get_fora_database["blacklist"]
approved_profile_banner = get_fora_database["approved_profile_banner"]
pending_profile_banner = get_fora_database["pending_profile_banner"]
get_sentinel_database = MongoClient(os.getenv('MONGO_URI'))['Sentinel']
warnings = get_sentinel_database["warnings"]
kicks = get_sentinel_database["kicks"]
bans = get_sentinel_database["bans"]

def blacklist_user_add(user_id: int, author_id: int, reason: str):
    """
    Adds a user to the Fora blacklist
    """
    get_fora_database["blacklist"].insert_one({
        "_id": user_id, 
        "time": str(datetime.date.today()),
        "author_id": author_id,
        "reason": reason
    })


def blacklist_user_remove(user_id: int):
    """
    Removes a user from the Fora blacklist
    """
    get_fora_database["blacklist"].delete_one({"_id": user_id})


def blacklist_user_get(user_id: int):
    """
    Returns a user from the Fora blacklist
    """
    return get_fora_database["blacklist"].find_one({"_id": user_id})
