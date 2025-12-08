import asyncio
import sys
from explorateur import RobotExplorateurAsync
from robots_db import init_db
from robots_manager import is_allowed
from utils import safe_scrape

class RobotExplorateurAvecRobots(RobotExplorateurAsync):
    async def scraper_page(self, session, url):
        return await safe_scrape(session, url, super().scraper_page)

if __name__ == "__main__":
    init_db()  # Initialise la base robots.txt
    explorateur = RobotExplorateurAvecRobots(concurrency=5)
    choix = input("Voulez-vous continuer la file d'attente existante ? (o/n) : ").strip().lower()
    if choix == 'o':
        url_depart = None  # Pas de nouvelle URL, on continue la file existante
    elif choix == 'n':
        url_depart = input("Entrez l'URL de départ (ex: https://exemple.com) : ").strip()
    else:
        print("Choix invalide. Veuillez répondre par 'o' ou 'n'.")
        sys.exit(1)
    try:
        asyncio.run(explorateur.commencer_exploration(url_depart))
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Arrêt demandé par l’utilisateur.")
        sys.exit(0)
