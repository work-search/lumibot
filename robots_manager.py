import aiohttp
from urllib.parse import urlparse
from typing import Optional
from robotexclusionrulesparser import RobotExclusionRulesParser
from robots_db import get_robots_from_db, store_robots_in_db


async def fetch_robots_txt(session: aiohttp.ClientSession, domain: str) -> Optional[str]:
    """
    Récupère le fichier robots.txt d'un domaine
    
    Args:
        session: Session aiohttp pour les requêtes HTTP
        domain: Nom de domaine (sans protocole)
        
    Returns:
        Contenu du robots.txt ou None si erreur/introuvable
    """
    robots_url = f"https://{domain}/robots.txt"
    try:
        async with session.get(robots_url, timeout=5) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"Erreur lors de la récupération du robots.txt pour {domain}: {e}")
    return None


async def is_allowed(session: aiohttp.ClientSession, url: str) -> bool:
    """
    Vérifie si le scraping d'une URL est autorisé selon robots.txt
    
    Args:
        session: Session aiohttp pour les requêtes HTTP
        url: URL complète à vérifier
        
    Returns:
        True si autorisé, False sinon
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    # 1. Vérifie en base
    robots_content = await get_robots_from_db(domain)

    # 2. Si pas en base, tente de le récupérer
    if robots_content is None:
        robots_content = await fetch_robots_txt(session, domain)
        if robots_content is not None:
            await store_robots_in_db(domain, robots_content)
        else:
            print(f"Aucun robots.txt trouvé pour {domain}, accès autorisé par défaut.")
            return True

    # 3. Parse les règles
    rerp = RobotExclusionRulesParser()
    rerp.parse(robots_content)
    return rerp.is_allowed("*", path)
