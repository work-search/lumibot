from urllib.parse import urlparse
from typing import List
from robots_manager import is_allowed


def contient_motif_interdit(url: str, motifs_interdits: List[str]) -> bool:
    """Vérifie si l'URL contient un caractère ou motif interdit"""
    for motif in motifs_interdits:
        if motif.lower() in url.lower():
            return True
    return False


def est_blackliste(url: str, blacklist_urls: List[str]) -> bool:
    """Vérifie si l'URL est dans la blacklist (y compris sous-domaines)"""
    netloc = urlparse(url).netloc.lower()
    for bl in blacklist_urls:
        bl_netloc = urlparse(bl).netloc.lower()
        if netloc == bl_netloc or netloc.endswith("." + bl_netloc):
            return True
    return False


def profondeur_url(url: str) -> int:
    """Retourne la profondeur du chemin d'une URL"""
    try:
        path = urlparse(url).path.strip("/")
        if not path:
            return 0
        return len(path.split("/"))
    except Exception:
        return 0


def est_url_valide(url: str, extensions_autorisees: List[str]) -> bool:
    """Vérifie si une URL est valide (HTTPS et extension autorisée)"""
    try:
        resultat = urlparse(url)
        if resultat.scheme != 'https':
            return False
        domaine = resultat.netloc.lower()
        return any(domaine.endswith(ext) for ext in extensions_autorisees)
    except Exception:
        return False


async def safe_scrape(session, url: str, scrape_func):
    """
    Effectue un scraping sécurisé en vérifiant d'abord les règles robots.txt
    
    Args:
        session: Session aiohttp pour les requêtes HTTP
        url: URL à scraper
        scrape_func: Fonction de scraping à appeler si autorisé
        
    Returns:
        Résultat du scraping ou None si interdit
    """
    if not await is_allowed(session, url):
        print(f"❌ Scraping interdit pour {url} (robots.txt)")
        return None
    print(f"✅ Scraping autorisé pour {url}")
    return await scrape_func(session, url)
