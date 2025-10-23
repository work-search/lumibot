"""
Configuration du logging pour Lumibot
"""
import logging
import os
from datetime import datetime


def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Configure le système de logging pour l'application
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Chemin vers le fichier de log (optionnel)
    """
    # Créer le répertoire de logs s'il n'existe pas
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Format des messages de log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configuration de base
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    # Logger pour les bibliothèques externes (moins verbeux)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger('lumibot')


def get_logger(name='lumibot'):
    """
    Récupère un logger configuré
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger configuré
    """
    return logging.getLogger(name)
