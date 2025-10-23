import asyncio
import sys
from explorateur import RobotExplorateurAsync
from robots_db import init_db
from robots_manager import is_allowed
from utils import safe_scrape
from logger import setup_logging, get_logger

# Configuration du logging
logger = setup_logging(log_file='logs/lumibot.log')

class RobotExplorateurAvecRobots(RobotExplorateurAsync):
    async def scraper_page(self, session, url):
        return await safe_scrape(session, url, super().scraper_page)

if __name__ == "__main__":
    async def main():
        """Fonction principale asynchrone"""
        logger.info("Démarrage de Lumibot...")
        await init_db()  # Initialise la base robots.txt de manière asynchrone
        explorateur = RobotExplorateurAvecRobots(concurrency=5)
        choix = input("Voulez-vous continuer la file d'attente existante ? (o/n) : ").strip().lower()
        if choix == 'o':
            url_depart = None  # Pas de nouvelle URL, on continue la file existante
            logger.info("Reprise de la file d'attente existante")
        elif choix == 'n':
            url_depart = input("Entrez l'URL de départ (ex: https://exemple.com) : ").strip()
            logger.info(f"Nouvelle exploration à partir de : {url_depart}")
        else:
            logger.error("Choix invalide. Veuillez répondre par 'o' ou 'n'.")
            print("Choix invalide. Veuillez répondre par 'o' ou 'n'.")
            sys.exit(1)
        try:
            await explorateur.commencer_exploration(url_depart)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Arrêt demandé par l'utilisateur")
            print("\n🛑 Arrêt demandé par l'utilisateur.")
            sys.exit(0)
    
    asyncio.run(main())
