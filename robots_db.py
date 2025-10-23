import aiosqlite
import os
from datetime import datetime
from typing import Optional


async def init_db() -> None:
    """Initialise la base de données robots.txt de manière asynchrone"""
    # Créer le répertoire database s'il n'existe pas
    os.makedirs("database", exist_ok=True)
    
    async with aiosqlite.connect("database/robots.db") as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS robots (
                domain TEXT PRIMARY KEY,
                content TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.commit()


async def get_robots_from_db(domain: str) -> Optional[str]:
    """Récupère le contenu robots.txt depuis la base de données de manière asynchrone"""
    async with aiosqlite.connect("database/robots.db") as conn:
        async with conn.execute("SELECT content FROM robots WHERE domain = ?", (domain,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None


async def store_robots_in_db(domain: str, content: str) -> None:
    """Stocke le contenu robots.txt dans la base de données de manière asynchrone"""
    async with aiosqlite.connect("database/robots.db") as conn:
        await conn.execute("""
            INSERT OR REPLACE INTO robots (domain, content, last_updated)
            VALUES (?, ?, ?)
        """, (domain, content, datetime.now()))
        await conn.commit()
