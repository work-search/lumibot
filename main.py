import asyncio
import sys
from explorateur import RobotExplorateurAsync

if __name__ == "__main__":
    explorateur = RobotExplorateurAsync(concurrency=5)
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
        print("\n Arret en cours...")
        sys.exit(0)

