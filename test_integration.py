"""
Tests d'intégration pour les fonctions asynchrones de Lumibot
"""
import unittest
import asyncio
import os
import tempfile
import shutil
from database import init_db, fermer_db
from robots_db import init_db as init_robots_db, get_robots_from_db, store_robots_in_db


class TestAsyncDatabase(unittest.TestCase):
    """Tests pour les fonctions de base de données asynchrones"""

    def setUp(self):
        """Préparation avant chaque test"""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test_sites.db')
        self.queue_path = os.path.join(self.test_dir, 'test_queue.db')
        self.robots_db = os.path.join(self.test_dir, 'test_robots.db')

    def tearDown(self):
        """Nettoyage après chaque test"""
        # Supprimer le répertoire temporaire
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_db_creates_tables(self):
        """Test de l'initialisation des tables de base de données"""
        async def run_test():
            conn, conn_file = await init_db(self.db_path, self.queue_path)
            
            # Vérifier que les tables existent
            async with conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                tables = await cursor.fetchall()
                table_names = [t[0] for t in tables]
                self.assertIn('pages', table_names)
            
            async with conn_file.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                tables = await cursor.fetchall()
                table_names = [t[0] for t in tables]
                self.assertIn('file_urls', table_names)
            
            await fermer_db(conn, conn_file)
        
        asyncio.run(run_test())

    def test_robots_db_operations(self):
        """Test des opérations sur la base robots.txt"""
        # Changer temporairement vers le répertoire de test
        original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        async def run_test():
            # Initialiser la base
            await init_robots_db()
            
            # Stocker un robots.txt
            test_domain = "example.com"
            test_content = "User-agent: *\nDisallow: /admin"
            await store_robots_in_db(test_domain, test_content)
            
            # Récupérer le robots.txt
            retrieved_content = await get_robots_from_db(test_domain)
            self.assertEqual(retrieved_content, test_content)
            
            # Tester un domaine inexistant
            non_existent = await get_robots_from_db("nonexistent.com")
            self.assertIsNone(non_existent)
        
        try:
            asyncio.run(run_test())
        finally:
            os.chdir(original_dir)


class TestAsyncUtils(unittest.TestCase):
    """Tests pour les fonctions utilitaires asynchrones"""

    def test_async_operations(self):
        """Test basique des opérations asynchrones"""
        async def simple_async_func():
            await asyncio.sleep(0.01)
            return "success"
        
        result = asyncio.run(simple_async_func())
        self.assertEqual(result, "success")


if __name__ == '__main__':
    unittest.main()
