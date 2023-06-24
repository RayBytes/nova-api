import setuptools
import os
import sqlite3
import argparse
import json

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='nova-api',
    version='0.0.1',
    author='Luna OSS',
    author_email='nsde@dmc.chat',
    description='Nova API Server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ]
)


with open('config.json', 'r') as file:
    config = json.load(file)

DB_PATH = os.getenv('DB_PATH') or config.get('DB_PATH')

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS keys (
                        key_value TEXT NOT NULL
                      );''')
    conn.commit()
    print("Database created!")

def add_key(key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO keys (key_value) VALUES (?)", (key,))
    conn.commit()
    print(f"Added key: {key}")

def remove_key(key_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM keys WHERE key_value=?", (key_id,))
    conn.commit()
    print(f"Removed key with key_id: {key_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NovaGPT Key Setup Utility")

    parser.add_argument('--create-db', action="store_true", help="Create the keys database")
    parser.add_argument('--add-key', type=str, help="Add a key to the keys database")
    parser.add_argument('--remove-key', type=int, help="Remove a key from the keys database by key_id")

    args = parser.parse_args()

    if args.create_db:
        create_database()
    elif args.add_key:
        add_key(args.add_key)
    elif args.remove_key:
        remove_key(args.remove_key)
    else:
        parser.print_help()


