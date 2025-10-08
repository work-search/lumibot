# Extensions et types autorisés/interdits
EXTENSIONS_AUTORISEES = [
    '.net', '.fr', '.com', '.eu', '.org', '.ovh', '.plus', '.dev',
    '.xyz', '.io', '.tech', '.site', '.store', '.shop', '.app', '.wiki'
]

EXTENSIONS_FICHIERS_INTERDITES = [
    # Commun
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',

    # Executables
    '.exe', '.msi', '.apk', '.ipa', '.dmg', '.iso',
    '.bat', '.sh', '.ps1', '.jar',

    # Videos/audio souvents lourds
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.webm',
    '.flac', '.wav',

    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.tiff', '.bmp',

    # Divers
    '.tmp', '.log', '.bak'
]

TYPES_CONTENU_AUTORISES = [
    'text/html',
    'application/xhtml+xml',
    'application/xml',   # ex: map du site, inutile et donc pas besoin de scraper ca
    'text/plain'         # ex: robots.txt sur youtube
]

# blacklist
BLACKLIST_URLS = [
    "https://www.google.com",
    "https://google.com",
    "https://www.facebook.com",
    "https://facebook.com",
    "https://www.youtube.com",
    "https://youtube.com",
    "https://wikipedia.org",
    "https://www.wikipedia.org",
    "https://github.com",
    "https://www.github.com",
    "https://trustpilot.com",
    "https://www.trustpilot.com",
    "https://pinterest.com",
    "https://www.pinterest.com",

    # anti-tracking
    "doubleclick.net",
    "googletagmanager.com",
    "google-analytics.com",
    "twitter.com",
    "instagram.com",
    "linkedin.com",
    "tiktok.com"
]

# Motifs interdits dans les URLs
MOTIFS_INTERDITS = [
    "?", "=", "&", "#", 
    "login", "signup", "register", "account", "auth", "signin", "logout", "session",
    "cart", "checkout", "payment", "wp-"
]

# En-têtes HTTP
EN_TETES = {
    'User-Agent': 'Lumibot/2.0 (https://github.com/work-search/api_princ)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}
