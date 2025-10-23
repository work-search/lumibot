"""
Tests unitaires pour les fonctions utilitaires de Lumibot
"""
import unittest
from utils import contient_motif_interdit, est_blackliste, profondeur_url, est_url_valide
from config import MOTIFS_INTERDITS, BLACKLIST_URLS, EXTENSIONS_AUTORISEES


class TestUtils(unittest.TestCase):
    """Tests pour les fonctions utilitaires"""

    def test_contient_motif_interdit(self):
        """Test de la détection des motifs interdits dans les URLs"""
        # URLs avec motifs interdits
        self.assertTrue(contient_motif_interdit("https://example.com/login", MOTIFS_INTERDITS))
        self.assertTrue(contient_motif_interdit("https://example.com/page?id=123", MOTIFS_INTERDITS))
        self.assertTrue(contient_motif_interdit("https://example.com/signup", MOTIFS_INTERDITS))
        self.assertTrue(contient_motif_interdit("https://example.com/cart", MOTIFS_INTERDITS))
        
        # URLs valides
        self.assertFalse(contient_motif_interdit("https://example.com/about", MOTIFS_INTERDITS))
        self.assertFalse(contient_motif_interdit("https://example.com/contact", MOTIFS_INTERDITS))

    def test_est_blackliste(self):
        """Test de la détection des URLs blacklistées"""
        # URLs blacklistées
        self.assertTrue(est_blackliste("https://www.google.com/search", BLACKLIST_URLS))
        self.assertTrue(est_blackliste("https://facebook.com/page", BLACKLIST_URLS))
        self.assertTrue(est_blackliste("https://www.youtube.com/watch", BLACKLIST_URLS))
        
        # URLs non blacklistées
        self.assertFalse(est_blackliste("https://example.com", BLACKLIST_URLS))
        self.assertFalse(est_blackliste("https://www.example.fr", BLACKLIST_URLS))

    def test_profondeur_url(self):
        """Test du calcul de profondeur d'URL"""
        self.assertEqual(profondeur_url("https://example.com"), 0)
        self.assertEqual(profondeur_url("https://example.com/"), 0)
        self.assertEqual(profondeur_url("https://example.com/page"), 1)
        self.assertEqual(profondeur_url("https://example.com/cat/page"), 2)
        self.assertEqual(profondeur_url("https://example.com/a/b/c"), 3)

    def test_est_url_valide(self):
        """Test de la validation d'URLs"""
        # URLs valides (HTTPS et extensions autorisées)
        self.assertTrue(est_url_valide("https://example.com", EXTENSIONS_AUTORISEES))
        self.assertTrue(est_url_valide("https://example.fr", EXTENSIONS_AUTORISEES))
        self.assertTrue(est_url_valide("https://example.org", EXTENSIONS_AUTORISEES))
        
        # URLs invalides (HTTP au lieu de HTTPS)
        self.assertFalse(est_url_valide("http://example.com", EXTENSIONS_AUTORISEES))
        
        # URLs invalides (extensions non autorisées)
        self.assertFalse(est_url_valide("https://example.de", EXTENSIONS_AUTORISEES))
        self.assertFalse(est_url_valide("https://example.ru", EXTENSIONS_AUTORISEES))


if __name__ == '__main__':
    unittest.main()
