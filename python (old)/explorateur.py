import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from config import *
from utils import *
from database import init_db, fermer_db
from langdetect import detect, LangDetectException

class RobotExplorateurAsync:
    def __init__(self, chemin_bdd='database/sites_web.db', chemin_file='database/file_attente.db', concurrency=5):
        self.chemin_bdd = chemin_bdd
        self.chemin_file = chemin_file
        self.concurrency = concurrency
        self.queue = asyncio.Queue()
        self.conn = None
        self.conn_file = None

    async def init_db(self):
        self.conn, self.conn_file = await init_db(self.chemin_bdd, self.chemin_file)

    async def ajouter_a_file(self, url):
        if est_blackliste(url, BLACKLIST_URLS):
            return
        if contient_motif_interdit(url, MOTIFS_INTERDITS):
            return
        if any(url.lower().endswith(ext) for ext in EXTENSIONS_FICHIERS_INTERDITES):
            return
        if profondeur_url(url) > 2:
            return

        # Vérifie si l'URL est déjà dans file_urls
        async with self.conn_file.execute("SELECT 1 FROM file_urls WHERE url = ?", (url,)) as cursor:
            if await cursor.fetchone():
                return

        # Vérifie si l'URL est déjà dans pages (déjà traitée)
        async with self.conn.execute("SELECT 1 FROM pages WHERE url = ?", (url,)) as cursor:
            if await cursor.fetchone():
                return

        # Si non, ajoute-la à la file
        await self.conn_file.execute(
            "INSERT INTO file_urls (url, statut) VALUES (?, 'en_attente')", (url,)
        )
        await self.conn_file.commit()
        await self.queue.put(url)



    async def sauvegarder_donnees_page(self, url, titre, description):
        if contient_motif_interdit(url, MOTIFS_INTERDITS):
            return
        await self.conn.execute(
            "INSERT OR REPLACE INTO pages (url, titre, description) VALUES (?, ?, ?)",
            (url, titre, description)
        )
        await self.conn.commit()
        print(f"[{datetime.now()}] 📥 Site ajouté : {url}")

    async def explorer_page(self, session, url):
        async with self.conn_file.execute("SELECT statut FROM file_urls WHERE url=?", (url,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] in ("terminee", "echouee"):
                return

        try:
            async with session.get(url, headers=EN_TETES) as resp:
                resp.raise_for_status()
                content_type = resp.headers.get('content-type', '').lower()
                if not any(t in content_type for t in TYPES_CONTENU_AUTORISES):
                    await self.marquer_url_echouee(url)
                    return

                text = await resp.text()
                soup = BeautifulSoup(text, 'html.parser')

                # Récupérer tout le texte utile pour la détection de langue
                texte_page = ' '.join([
                    p.get_text(strip=True)
                    for p in soup.find_all('p')
                    if not p.find_parent(['header', 'footer', 'nav'])
                ])

                # Détecter la langue si le texte est suffisamment long
                if len(texte_page.split()) > 10:  # Seuil minimal pour éviter les faux positifs
                    try:
                        langue_detectee = detect(texte_page)
                        if langue_detectee != 'fr':
                            print(f"[{datetime.now()}] ⚠️ Page non francophone détectée : {url} (langue: {langue_detectee})")
                            await self.marquer_url_echouee(url)
                            return
                        #else:
                            #print(f"[{datetime.now()}] ✅ Page francophone confirmée : {url} (langue: {langue_detectee})")
                    except LangDetectException:
                        print(f"[{datetime.now()}] ℹ️ Détection de langue impossible pour {url}, traitement continué.")
                        pass  # Si la détection échoue, on continue


                # Traitement normal si la page est francophone ou si la détection a échoué
                titre = soup.title.string.strip() if soup.title else ''
                description_meta = soup.find('meta', attrs={'name': 'description'})
                meta_desc = description_meta['content'].strip() if description_meta else ''
                contenu = []
                for tag in soup.find_all(['h1', 'h2', 'h3']):
                    t = tag.get_text(strip=True)
                    if t:
                        contenu.append(t)
                for p in soup.find_all('p'):
                    if p.find_parent(['header', 'footer', 'nav']):
                        continue
                    texte = p.get_text(strip=True)
                    nb_mots = len(texte.split())
                    if 3 <= nb_mots <= 150:
                        contenu.append(texte)
                description = "\n".join([titre, meta_desc] + contenu)
                await self.sauvegarder_donnees_page(url, titre, description)

                # Ajouter les liens trouvés à la file
                for lien in soup.find_all('a', href=True):
                    nouvelle_url = urljoin(url, lien['href'])
                    if est_url_valide(nouvelle_url, EXTENSIONS_AUTORISEES):
                        await self.ajouter_a_file(nouvelle_url)

                await self.marquer_url_terminee(url)

        except Exception as e:
            print(f"[{datetime.now()}] ❌ Erreur lors de l'exploration de {url}: {e}")
            await self.marquer_url_echouee(url)

                                  
                                
    async def marquer_url_terminee(self, url):
        await self.conn_file.execute("UPDATE file_urls SET statut='terminee' WHERE url=?", (url,))
        await self.conn_file.commit()

    async def marquer_url_echouee(self, url):
        await self.conn_file.execute("UPDATE file_urls SET statut='echouee' WHERE url=?", (url,))
        await self.conn_file.commit()

    async def worker(self):
        async with aiohttp.ClientSession() as session:
            while True:
                url = await self.queue.get()
                await self.explorer_page(session, url)
                self.queue.task_done()

    async def commencer_exploration(self, url_depart=None, max_pages=100):
        await self.init_db()
        if url_depart and est_url_valide(url_depart, EXTENSIONS_AUTORISEES):
            await self.ajouter_a_file(url_depart)
        # Charge les URLs en attente depuis la base de données
        async with self.conn_file.execute("SELECT url FROM file_urls WHERE statut='en_attente'") as cursor:
            async for row in cursor:
                await self.queue.put(row[0])
        workers = [asyncio.create_task(self.worker()) for _ in range(self.concurrency)]
        try:
            await self.queue.join()
        except asyncio.CancelledError:
            print("⚠️ Exploration interrompue.")
            raise
        finally:
            for w in workers:
                w.cancel()
            await fermer_db(self.conn, self.conn_file)
