import aiosqlite
import os
from datetime import datetime
from typing import Tuple, Optional


async def init_db(chemin_bdd: str, chemin_file: str) -> Tuple[aiosqlite.Connection, aiosqlite.Connection]:
    async with aiosqlite.connect(chemin_bdd) as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                titre TEXT,
                description TEXT,
                horodatage DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await conn.commit()

    async with aiosqlite.connect(chemin_file) as conn_file:
        await conn_file.execute('''
            CREATE TABLE IF NOT EXISTS file_urls (
                url TEXT PRIMARY KEY,
                heure_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
                statut TEXT DEFAULT 'en_attente'
            )
        ''')
        # Ajout d’un index pour les recherches rapides sur statut
        await conn_file.execute('CREATE INDEX IF NOT EXISTS idx_file_statut ON file_urls(statut)')
        await conn_file.commit()

    # On réouvre les connexions pour les renvoyer
    conn = await aiosqlite.connect(chemin_bdd)
    conn_file = await aiosqlite.connect(chemin_file)

    # Petites optis SQLite
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn_file.execute("PRAGMA journal_mode=WAL")

    return conn, conn_file


async def fermer_db(conn: Optional[aiosqlite.Connection], conn_file: Optional[aiosqlite.Connection]) -> None:
    if conn:
        await conn.close()
    if conn_file:
        await conn_file.close()
