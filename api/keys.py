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
    cache = {}

    # Initialize MongoDB
    client = MongoClient(MONGO_URI)
    db = client.get_database('keys_db')
    collection = db['keys']

    def __init__(self, key: str, model: str):
        self.key = key
        self.model = model
        if not Keys.cache:
            self._load_keys()

    def _load_keys(self) -> None:
        cursor = Keys.collection.find({}, {'_id': 0, 'key_value': 1, 'model': 1})
        for doc in cursor:
            key_value = doc['key_value']
            model = doc['model']
            Keys.cache.setdefault(model, set()).add(key_value)

    def lock(self) -> None:
        self.locked_keys.add(self.key)

    def unlock(self) -> None:
        self.locked_keys.remove(self.key)

    def is_locked(self) -> bool:
        return self.key in self.locked_keys

    @staticmethod
    def get(model: str) -> str:
        key_candidates = list(Keys.cache.get(model, set()))
        random.shuffle(key_candidates)

        for key_candidate in key_candidates:
            key = Keys(key_candidate, model)

            if not key.is_locked():
                key.lock()
                return key.key

        print(f"[WARN] No unlocked keys found for model '{model}' in get keys request!")

    def delete(self) -> None:
        Keys.collection.delete_one({'key_value': self.key, 'model': self.model})
        # Update cache
        try:
            Keys.cache[self.model].remove(self.key)
        except KeyError:
            print(f"[WARN] Tried to remove a key from cache which was not present: {self.key}")

    def save(self) -> None:
        Keys.collection.insert_one({'key_value': self.key, 'model': self.model})
        # Update cache
        Keys.cache.setdefault(self.model, set()).add(self.key)

# Usage example:
# os.environ['MONGO_URI'] = "mongodb://localhost:27017"
# key_instance = Keys("example_key", "example_model")
# key_instance.save()
# key_value = Keys.get("example_model")
