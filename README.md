# Lumibot

Lumibot est un robot d'exploration web asynchrone conçu pour collecter des informations à partir de sites web, en respectant les règles `robots.txt` et en se concentrant sur le contenu francophone, dans l'objectif de créer une db pour [lumina](https://github.com/work-search/moteur-recherche-lumina). Il utilise `aiohttp` pour des requêtes HTTP efficaces et `BeautifulSoup` pour le parsing HTML, stockant les données collectées dans une base de données SQLite.

## Fonctionnalités

*   **Exploration Asynchrone**: Utilise `asyncio` et `aiohttp` pour une exploration rapide et concurrente.
*   **Respect de `robots.txt`**: Vérifie et applique les règles `robots.txt` pour chaque domaine, en mettant en cache les règles pour optimiser les performances.
*   **Filtrage de Contenu**: Ignore les URLs blacklistées, les motifs d'URL interdits, les extensions de fichiers non pertinentes et limite la profondeur d'exploration.
*   **Détection de Langue**: Détecte la langue des pages explorées et ne traite que le contenu francophone.
*   **Extraction de Données**: Extrait le titre, la méta-description et le contenu textuel pertinent (titres H1-H3, paragraphes) des pages HTML.
*   **Persistance des Données**: Stocke les URLs explorées et les données extraites dans des bases de données SQLite (`sites_web.db` pour les pages, `file_attente.db` pour la file d'attente).
*   **Reprise d'Exploration**: Permet de reprendre une exploration interrompue à partir de la file d'attente existante.

## Installation

Pour installer et exécuter Lumibot, suivez les étapes ci-dessous :

1.  **Cloner le dépôt** :

    ```bash
    git clone https://github.com/work-search/lumibot.git
    cd lumibot
    ```

2.  **Installer les dépendances** :

    ```bash
    pip install -r requirements.txt
    ```

## Tests

Pour exécuter les tests unitaires :

```bash
python3 -m unittest test_utils.py -v
```

Ou avec pytest (si installé) :

```bash
pytest test_utils.py -v
```

## Utilisation

Pour démarrer le robot d'exploration :

```bash
python3.11 main.py
```

Le programme vous demandera si vous souhaitez continuer une file d'attente existante (`o/n`).

*   Si vous choisissez `o` (oui), le robot reprendra l'exploration à partir des URLs en attente dans `file_attente.db`.
*   Si vous choisissez `n` (non), il vous sera demandé de fournir une URL de départ pour une nouvelle exploration.

## Structure du Projet

*   `main.py`: Le point d'entrée principal du robot, initialise la base de données et lance l'exploration.
*   `explorateur.py`: Contient la logique principale du robot d'exploration, y compris la gestion de la file d'attente, le scraping des pages, l'extraction de liens et la détection de langue.
*   `database.py`: Gère l'initialisation et la fermeture des bases de données SQLite pour les pages explorées et la file d'attente.
*   `robots_manager.py`: S'occupe de la récupération et de l'application des règles `robots.txt`.
*   `robots_db.py`: Gère la persistance des règles `robots.txt` dans une base de données.
*   `config.py`: Contient les configurations globales telles que les en-têtes HTTP, les URLs blacklistées, les motifs interdits, les extensions de fichiers autorisées/interdites, etc.
*   `utils.py`: Fournit des fonctions utilitaires comme la validation d'URL, le scraping sécurisé et la gestion des profondeurs d'URL.

## Configuration

Le fichier `config.py` contient plusieurs paramètres configurables pour ajuster le comportement du robot. Vous pouvez modifier :

*   `BLACKLIST_URLS`: Liste d'URLs à ignorer.
*   `MOTIFS_INTERDITS`: Liste de motifs d'URL à éviter.
*   `EXTENSIONS_FICHIERS_INTERDITES`: Extensions de fichiers à ne pas explorer.
*   `TYPES_CONTENU_AUTORISES`: Types de contenu MIME autorisés.
*   `EN_TETES`: En-têtes HTTP utilisés pour les requêtes.

## Licence

Ce projet est sous licence [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html).

## Contact

En cas de problème avec le scraping du bot sur votre site, veuillez contacter :

*   **Discord**: [https://discord.gg/QkwWDKeMjF](https://discord.gg/QkwWDKeMjF)
*   **Email**: [axel@athenox.dev](mailto:axel@athenox.dev)
