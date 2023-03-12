from tortoise import Tortoise

from . import data
from .data import Data
from pathlib import Path

DB_PATH = Path(__file__).parent / "db.sqlite3"
DATABASE = {
    "connections": {
        "database": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": DB_PATH},
        }
    },
    "apps": {
        "data": {
            "models": [data.__name__],
            "default_connection": "database",
        },
    },
}


async def connect():
    """
    连接数据库
    """
    await Tortoise.init(DATABASE)
    await Tortoise.generate_schemas()


async def disconnect():
    await Tortoise.close_connections()
