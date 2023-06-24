import json
import os
import random
from pymongo import MongoClient

with open('./config.json', 'r') as file:
    config = json.load(file)

class Keys:
    # --- START OF CONFIG ---
    MONGO_URI = os.getenv('MONGO_URI') or config.get('MONGO_URI')
    # --- END OF CONFIG ---

    locked_keys = set()
    cache = set()

    # Initialize MongoDB
    client = MongoClient(MONGO_URI)
    db = client.get_database('keys_db')
    collection = db['keys']

    def __init__(self, key: str):
        self.key = key
        if not Keys.cache:
            self._load_keys()

    def _load_keys(self) -> None:
        cursor = self.collection.find({}, {'_id': 0, 'key_value': 1})
        for doc in cursor:
            key_value = doc['key_value']
            self.cache.add(key_value)

    def lock(self) -> None:
        self.locked_keys.add(self.key)

    def unlock(self) -> None:
        self.locked_keys.remove(self.key)

    def is_locked(self) -> bool:
        return self.key in self.locked_keys

    def get() -> str:
        key_candidates = list(Keys.cache)
        random.shuffle(key_candidates)

        for key_candidate in key_candidates:
            key = Keys(key_candidate)

            if not key.is_locked():
                key.lock()
                return key.key

        print("[WARN] No unlocked keys found in get keys request!")

    def delete(self) -> None:
        self.collection.delete_one({'key_value': self.key})
        # Update cache
        try:
            Keys.cache.remove(self.key)
        except KeyError:
            print("[WARN] Tried to remove a key from cache which was not present: " + self.key)

    def save(self) -> None:
        self.collection.insert_one({'key_value': self.key})
        # Update cache
        Keys.cache.add(self.key)

# Usage example:
# os.environ['MONGO_URI'] = "mongodb://localhost:27017"
# key_instance = Keys("example_key")
# key_instance.save()
# key_value = Keys.get()
