import json
import os
import random
import time
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

    def __init__(self, key: str, model: str, provider_name: str, ratelimit: int, url: str):
        self.key = key
        self.model = model
        self.provider_name = provider_name
        self.ratelimit = ratelimit
        self.url = url
        if not Keys.cache:
            self._load_keys()

    def _load_keys(self) -> None:
        cursor = Keys.collection.find({}, {'_id': 0, 'key_value': 1, 'model': 1, 'provider_name': 1, 'ratelimit': 1, 'url': 1, 'last_used': 1})
        for doc in cursor:
            key_value = doc['key_value']
            model = doc['model']
            provider_name = doc['provider_name']
            ratelimit = doc['ratelimit']
            url = doc['url']
            last_used = doc.get('last_used', 0)
            key_data = {'provider_name': provider_name, 'ratelimit': ratelimit, 'url': url, 'last_used': last_used}
            Keys.cache.setdefault(model, {}).setdefault(key_value, key_data)

    def lock(self) -> None:
        self.locked_keys.add(self.key)

    def unlock(self) -> None:
        self.locked_keys.remove(self.key)

    def is_locked(self) -> bool:
        return self.key in self.locked_keys

    @staticmethod
    def get(model: str) -> str:
        key_candidates = list(Keys.cache.get(model, {}).keys())
        random.shuffle(key_candidates)

        current_time = time.time()

        for key_candidate in key_candidates:
            key_data = Keys.cache[model][key_candidate]
            key = Keys(key_candidate, model, key_data['provider_name'], key_data['ratelimit'], key_data['url'])
            time_since_last_used = current_time - key_data.get('last_used', 0)

            if not key.is_locked() and time_since_last_used >= key.ratelimit:
                key.lock()
                key_data['last_used'] = current_time  # Update last_used in the cache
                Keys.collection.update_one(
                    {'key_value': key.key, 'model': key.model},
                    {'$set': {'last_used': current_time}}  # Update last_used in the database
                )
                return {
                    'url': key.url,
                    'key_value': key.key
                }

        print(f"[WARN] No unlocked keys found for model '{model}' in get keys request!")

    def delete(self) -> None:
        Keys.collection.delete_one({'key_value': self.key, 'model': self.model})
        # Update cache
        try:
            del Keys.cache[self.model][self.key]
        except KeyError:
            print(f"[WARN] Tried to remove a key from cache which was not present: {self.key}")

    def save(self) -> None:
        key_data = {
            'provider_name': self.provider_name,
            'ratelimit': self.ratelimit,
            'url': self.url,
            'last_used': 0  # Initialize last_used to 0 when saving a new key
        }
        Keys.collection.insert_one({'key_value': self.key, 'model': self.model, **key_data})
        # Update cache
        Keys.cache.setdefault(self.model, {}).setdefault(self.key, key_data)

# Usage example:
# os.environ['MONGO_URI'] = "mongodb://localhost:27017"
# key_instance = Keys("example_key", "gpt-4", "openai", "10", "https://whatever-openai-thing-is/chat/completions/")
# key_instance.save()
# key_value = Keys.get("gpt-4")


