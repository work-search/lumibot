import asyncio
import sys
from explorateur import RobotExplorateurAsync

if __name__ == "__main__":
    explorateur = RobotExplorateurAsync(concurrency=5)
    url_depart = input("Entrez l'URL de départ (ex: https://exemple.com): ")
    try:
        asyncio.run(explorateur.commencer_exploration(url_depart))
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Arrêt demandé par l’utilisateur.")
        sys.exit(0)
