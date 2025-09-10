# Extensions et types autorisés/interdits
EXTENSIONS_AUTORISEES = ['.net', '.fr', '.com', '.eu', '.org', 'ovh', '.plus', '.dev', '.xyz', '.io']
EXTENSIONS_FICHIERS_INTERDITES = [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.7z',
    '.exe', '.msi', '.apk', '.ipa', '.dmg', '.iso', '.mp3', '.mp4',
    '.avi', '.mov', '.jpg', '.jpeg', '.png', '.gif', '.svg'
]
TYPES_CONTENU_AUTORISES = ['text/html', 'application/xhtml+xml']

# Blacklist URLs ou domaines
BLACKLIST_URLS = [
    "https://www.google.com",
    "https://www.facebook.com",
    "https://www.youtube.com",
    "https://google.com",
    "https://facebook.com",
    "https://youtube.com",
    "https://wikipedia.org",
    "https://www.wikipedia.org",
    "https://github.com",
    "https://www.github.com",
    "https://trustpilot.com",
    "https://www.trustpilot.com"
]

# Motifs interdits dans les URLs
MOTIFS_INTERDITS = [
    "?", "=", "&", "#", "login", "signup", "register", "account", "wp-"
]

# En-têtes HTTP
EN_TETES = {
    'User-Agent': 'Lumibot/2.0 (https://github.com/work-search/api_princ)'
}
