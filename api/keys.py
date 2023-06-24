import json
import os
import random
import sqlite3

with open('./config.json', 'r') as file:
    config = json.load(file)

class Keys:
    # --- START OF CONFIG ---

    DB_PATH = os.getenv('DB_PATH') or config.get('DB_PATH')

    # --- END OF CONFIG ---

    locked_keys = set()
    cache = set()

    def __init__(self, key: str):
        self.key = key
        if not Keys.cache:
            self._load_keys()

    def _connect(self):
        conn = sqlite3.connect(self.DB_PATH)
        return conn

    def _load_keys(self) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT key_value FROM keys")
        rows = cursor.fetchall()
        for row in rows:
            key_value = row[0]
            self.cache.add(key_value)
        conn.commit()

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
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM keys WHERE key_value=?", (self.key,))
        conn.commit()
        # Update cache
        try:
            Keys.cache.remove(self.key)
        except KeyError:
            print("[WARN] Tried to remove a key from cache which was not present: " + self.key)

    def save(self) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO keys (key_value) VALUES (?)", (self.key,))
        conn.commit()
        # Update cache
        Keys.cache.add(self.key)


# Usage example:
# os.environ['DB_PATH'] = "keys.db"
# key_instance = Keys("example_ky")
# key_instance.save()
# key_value = Keys.get()

