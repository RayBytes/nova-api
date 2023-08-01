"""Database helper."""

import os
import aiosqlite

from dotenv import load_dotenv

load_dotenv()

async def row_to_dict(row, cursor):
    """Converts a database row to into a <dict>."""    

    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

async def connect(name: str):
    """Creates a connection to the database"""

    return await aiosqlite.connect(f'{os.getenv("API_DB_PATH")}{name}.db')

async def insert_dict(dict_: dict, table: str, db) -> dict:
    """Adds a dictionary to a table, safely."""

    if isinstance(db, str):
        db = await connect(db)

    sep = ', '
    query = f"""
        INSERT INTO {table} ({sep.join(dict_.keys())})
        VALUES ({sep.join([f':{key}' for key in dict_.keys()])})
    """

    await db.execute(query, dict_)
    await db.commit()
    
    return dict_

