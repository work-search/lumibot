import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime


class RobotExplorateur:
    def __init__(self, chemin_bdd='sites_web.db', chemin_file='file_attente.db'):
        print(f"[{datetime.now()}] Initialisation du robot explorateur...")
        self.conn = sqlite3.connect(chemin_bdd)
        self.cur = self.conn.cursor()
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                titre TEXT,
                description TEXT,
                horodatage DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn_file = sqlite3.connect(chemin_file)
        self.cur_file = self.conn_file.cursor()
        self.cur_file.execute('''
            CREATE TABLE IF NOT EXISTS file_urls (
                url TEXT PRIMARY KEY,
                heure_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
                statut TEXT DEFAULT 'en_attente'
            )
        ''')

        self.cur_file.execute('''
            CREATE TABLE IF NOT EXISTS statut_explorateur (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                pages_explorees INTEGER DEFAULT 0,
                derniere_execution DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.en_tetes = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        self.extensions_autorisees = ['.net', '.fr', '.com', '.eu', '.org', 'ovh', '.plus', '.dev', '.xyz']
        self.types_contenu_autorises = ['text/html', 'application/xhtml+xml']
        self.extensions_fichiers_interdites = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.7z',
            '.exe', '.msi', '.apk', '.ipa', '.dmg', '.iso', '.mp3', '.mp4',
            '.avi', '.mov', '.jpg', '.jpeg', '.png', '.gif', '.svg'
        ]

    def obtenir_statut_explorateur(self):
        self.cur_file.execute('SELECT pages_explorees FROM statut_explorateur WHERE id = 1')
        resultat = self.cur_file.fetchone()
        if resultat is None:
            self.cur_file.execute('INSERT INTO statut_explorateur (id, pages_explorees) VALUES (1, 0)')
            self.conn_file.commit()
            return 0
        return resultat[0]

    def mettre_a_jour_statut(self, pages_explorees):
        self.cur_file.execute('''
            INSERT OR REPLACE INTO statut_explorateur (id, pages_explorees, derniere_execution)
            VALUES (1, ?, CURRENT_TIMESTAMP)
        ''', (pages_explorees,))
        self.conn_file.commit()

    def ajouter_a_file(self, url):
        if any(url.lower().endswith(ext) for ext in self.extensions_fichiers_interdites):
            return
        self.cur_file.execute('''
            INSERT OR IGNORE INTO file_urls (url, statut)
            VALUES (?, 'en_attente')
        ''', (url,))
        self.conn_file.commit()

    def obtenir_prochaine_url(self):
        self.cur_file.execute('''
            SELECT url FROM file_urls 
            WHERE statut = 'en_attente' 
            ORDER BY heure_ajout ASC LIMIT 1
        ''')
        resultat = self.cur_file.fetchone()
        if resultat:
            url = resultat[0]
            self.cur_file.execute('''
                UPDATE file_urls 
                SET statut = 'en_cours' 
                WHERE url = ?
            ''', (url,))
            self.conn_file.commit()
            return url
        return None

    def marquer_url_terminee(self, url):
        self.cur_file.execute('''
            UPDATE file_urls 
            SET statut = 'terminee' 
            WHERE url = ?
        ''', (url,))
        self.conn_file.commit()

    def marquer_url_echouee(self, url):
        self.cur_file.execute('''
            UPDATE file_urls 
            SET statut = 'echouee' 
            WHERE url = ?
        ''', (url,))
        self.conn_file.commit()

    def est_url_valide(self, url):
        try:
            resultat = urlparse(url)
            if resultat.scheme != 'https':
                return False
            domaine = resultat.netloc.lower()
            return any(domaine.endswith(ext) for ext in self.extensions_autorisees)
        except:
            return False

    def sauvegarder_donnees_page(self, url, titre, description):
        self.cur.execute('''
            INSERT OR REPLACE INTO pages (url, titre, description)
            VALUES (?, ?, ?)
        ''', (url, titre, description))
        self.conn.commit()
        print(f"[{datetime.now()}] 📥 Site ajouté à la base de données : {url}")

    def est_contenu_html(self, headers):
        content_type = headers.get('content-type', '').lower()
        return any(type_autorise in content_type for type_autorise in self.types_contenu_autorises)

    def explorer_page(self, url):
        try:
            reponse_head = requests.head(url, headers=self.en_tetes, timeout=10, allow_redirects=True)
            if not self.est_contenu_html(reponse_head.headers):
                self.marquer_url_echouee(url)
                return False

            reponse = requests.get(url, headers=self.en_tetes, timeout=10)
            reponse.raise_for_status()

            if not self.est_contenu_html(reponse.headers):
                self.marquer_url_echouee(url)
                return False

            soup = BeautifulSoup(reponse.text, 'html.parser')
            titre = soup.title.string if soup.title else ''
            description_meta = soup.find('meta', attrs={'name': 'description'})
            description = description_meta['content'] if description_meta else ''
            if not description:
                description = titre

            self.sauvegarder_donnees_page(url, titre, description)

            for lien in soup.find_all('a', href=True):
                nouvelle_url = urljoin(url, lien['href'])
                if self.est_url_valide(nouvelle_url):
                    self.ajouter_a_file(nouvelle_url)

            self.marquer_url_terminee(url)
            return True
        except Exception as e:
            self.marquer_url_echouee(url)
            return False

    def commencer_exploration(self, url_depart=None, max_pages=100):
        print(f"[{datetime.now()}] 🚀 Démarrage de l'exploration")
        if url_depart and self.est_url_valide(url_depart):
            print(f"[{datetime.now()}] ✅ URL de départ valide: {url_depart}")
            self.ajouter_a_file(url_depart)
        elif url_depart:
            print(f"[{datetime.now()}] ❌ URL de départ invalide: {url_depart}")
            return

        pages_explorees = self.obtenir_statut_explorateur()
        print(f"[{datetime.now()}] 📊 Reprise depuis {pages_explorees} pages explorées")

        while pages_explorees < max_pages:
            url = self.obtenir_prochaine_url()
            if not url:
                print(f"[{datetime.now()}] ⚠️ Plus d'URLs dans la file d'attente")
                break

            if self.explorer_page(url):
                pages_explorees += 1
                self.mettre_a_jour_statut(pages_explorees)
                print(f"[{datetime.now()}] ✨ Exploration réussie ({pages_explorees}/{max_pages} pages)")

            # print(f"[{datetime.now()}] 😴 Pause d'une seconde...")
            # time.sleep(1)

    def fermer(self):
        self.conn.close()
        self.conn_file.close()
        print(f"[{datetime.now()}] 👋 Fermeture des connexions aux bases de données")


if __name__ == "__main__":
    print(f"[{datetime.now()}] 🤖 Démarrage du robot explorateur")
    explorateur = RobotExplorateur()
    try:
        explorateur.cur_file.execute("SELECT COUNT(*) FROM file_urls WHERE statut = 'en_attente'")
        nombre_en_attente = explorateur.cur_file.fetchone()[0]

        if nombre_en_attente > 0:
            print(f"[{datetime.now()}] 📊 Trouvé {nombre_en_attente} URLs en attente dans la file")
            reprendre = input("Voulez-vous reprendre l'exploration précédente ? (o/n): ").lower()
            if reprendre == 'o':
                max_pages = int(input("Entrez le nombre maximum de pages à explorer: "))
                explorateur.commencer_exploration(max_pages=max_pages)
            else:
                url_depart = input("Entrez l'URL de départ (ex: https://exemple.com): ")
                max_pages = int(input("Entrez le nombre maximum de pages à explorer: "))
                explorateur.commencer_exploration(url_depart, max_pages)
        else:
            url_depart = input("Entrez l'URL de départ (ex: https://exemple.com): ")
            max_pages = int(input("Entrez le nombre maximum de pages à explorer: "))
            explorateur.commencer_exploration(url_depart, max_pages)
    finally:
        explorateur.fermer()
