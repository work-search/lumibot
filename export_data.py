import aiosqlite
import requests
from config import *
import asyncio
import os

API_URL = "https://marvideo.fr/lumina/?action=add"
BATCH_SIZE = 100

async def get_pages():
    pages = []
    async with aiosqlite.connect("database/sites_web.db") as conn:
        async with conn.execute("SELECT * FROM pages") as cursor:
            async for row in cursor:
                pages.append({
                    "url": row[0],
                    "titre": row[1],
                    "description": row[2]
                })
    return pages

def send_batch(batch, idx):
    try:
        r = requests.post(API_URL, json=batch, headers=EN_TETES, timeout=10)
        r.raise_for_status()
        print(f"[OK] Batch {idx} ({len(batch)} pages) → {r.json()}")
    except Exception as e:
        print(f"[ERREUR] Batch {idx} → {e}")

async def main():
    pages = await get_pages()
    if not pages:
        print("[INFO] Aucune page à envoyer.")
        return
    for i in range(0, len(pages), BATCH_SIZE):
        batch = pages[i:i+BATCH_SIZE]
        send_batch(batch, i // BATCH_SIZE + 1)
    os.remove("database/sites_web.db")

if __name__ == "__main__":
    asyncio.run(main())