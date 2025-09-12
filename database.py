import aiosqlite
import os
from datetime import datetime

async def init_db(chemin_bdd, chemin_file):
    try:
        os.mkdir("database")
    except:
        print("")
    conn = await aiosqlite.connect(chemin_bdd)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            url TEXT PRIMARY KEY,
            titre TEXT,
            description TEXT,
            horodatage DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    await conn.commit()

    conn_file = await aiosqlite.connect(chemin_file)
    await conn_file.execute('''
        CREATE TABLE IF NOT EXISTS file_urls (
            url TEXT PRIMARY KEY,
            heure_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'en_attente'
        )
    ''')
    await conn_file.commit()
    return conn, conn_file

async def fermer_db(conn, conn_file):
    if conn:
        await conn.close()
    if conn_file:
        await conn_file.close()
