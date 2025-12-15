"""
Script de migration vers SQLite FTS5
====================================
Ce script migre votre base de données existante vers une version avec Full-Text Search.

Usage:
    python migrate_to_fts5.py [chemin_vers_db]
    
Par défaut, utilise: database/sites_web.db
"""

import sqlite3
import os
import sys


def print_progress(current, total, bar_length=40):
    """Affiche une barre de progression."""
    percent = current / total if total > 0 else 1
    filled = int(bar_length * percent)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f'\r📥 Indexation: [{bar}] {percent*100:.1f}% ({current}/{total})', end='', flush=True)


def migrate_to_fts5(db_path: str):
    """
    Migre la base de données vers FTS5.
    """
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 2. Vérifier si FTS5 existe déjà
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pages_fts'")
        if cursor.fetchone():
            print("⚠️ La table FTS5 existe déjà. Migration annulée.")
            conn.close()
            return True
        
        # 3. Compter les entrées existantes
        cursor.execute("SELECT COUNT(*) FROM pages")
        total = cursor.fetchone()[0]
        print(f"📊 {total} pages à indexer...")
        
        # 4. Créer la table FTS5
        print("🔧 Création de la table FTS5...")
        cursor.execute("""
            CREATE VIRTUAL TABLE pages_fts USING fts5(
                titre,
                description,
                content='pages',
                content_rowid='rowid'
            )
        """)
        
        # 5. Créer les triggers pour synchronisation automatique
        print("🔧 Création des triggers de synchronisation...")
        
        # Trigger INSERT
        cursor.execute("""
            CREATE TRIGGER pages_ai AFTER INSERT ON pages BEGIN
                INSERT INTO pages_fts(rowid, titre, description)
                VALUES (new.rowid, new.titre, new.description);
            END
        """)
        
        # Trigger DELETE
        cursor.execute("""
            CREATE TRIGGER pages_ad AFTER DELETE ON pages BEGIN
                INSERT INTO pages_fts(pages_fts, rowid, titre, description)
                VALUES ('delete', old.rowid, old.titre, old.description);
            END
        """)
        
        # Trigger UPDATE
        cursor.execute("""
            CREATE TRIGGER pages_au AFTER UPDATE ON pages BEGIN
                INSERT INTO pages_fts(pages_fts, rowid, titre, description)
                VALUES ('delete', old.rowid, old.titre, old.description);
                INSERT INTO pages_fts(rowid, titre, description)
                VALUES (new.rowid, new.titre, new.description);
            END
        """)
        
        # 6. Indexer les données existantes avec progression (Mode Streaming)
        print("📥 Indexation des données existantes...")
        
        # On utilise le curseur comme itérateur pour ne pas charger la RAM
        cursor.execute("SELECT rowid, titre, description FROM pages")
        
        BATCH_SIZE = 10000
        
        for i, (rowid, titre, description) in enumerate(cursor, 1):
            cursor.execute(
                "INSERT INTO pages_fts(rowid, titre, description) VALUES (?, ?, ?)",
                (rowid, titre, description)
            )
            
            # Mise à jour progression
            if i % 1000 == 0:
                print_progress(i, total)
                
            # Commit partiel tous les 50 000 items pour libérer la mémoire/disque
            if i % 50000 == 0:
                conn.commit()
        
        print_progress(total, total) # 100% à la fin
        print()  # Nouvelle ligne après la barre de progression
        
        # 7. Optimiser l'index FTS5
        print("⚡ Optimisation de l'index...")
        cursor.execute("INSERT INTO pages_fts(pages_fts) VALUES('optimize')")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Migration terminée avec succès!")
        print(f"   - {total} pages indexées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False


def test_fts5(db_path: str, query: str = "test"):
    """Teste la recherche FTS5."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n🔍 Test de recherche FTS5 pour: '{query}'")
    
    cursor.execute("""
        SELECT p.url, p.titre, snippet(pages_fts, 1, '<b>', '</b>', '...', 20) as extrait
        FROM pages_fts
        JOIN pages p ON pages_fts.rowid = p.rowid
        WHERE pages_fts MATCH ?
        LIMIT 5
    """, (query,))
    
    results = cursor.fetchall()
    if results:
        print(f"   Trouvé {len(results)} résultat(s):")
        for url, titre, extrait in results:
            print(f"   - {titre[:50]}...")
    else:
        print("   Aucun résultat trouvé.")
    
    conn.close()


if __name__ == "__main__":
    # Chemin par défaut ou argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'sites_web.db')
    
    print("=" * 50)
    print("  Migration SQLite vers FTS5")
    print("=" * 50)
    print(f"📁 Base de données: {db_path}")
    print()
    
    confirm = input("Voulez-vous continuer la migration ? (o/n): ").strip().lower()
    if confirm == 'o':
        if migrate_to_fts5(db_path):
            test_query = input("\nTester la recherche FTS5 ? Entrez un mot (ou Entrée pour passer): ").strip()
            if test_query:
                test_fts5(db_path, test_query)
    else:
        print("Migration annulée.")
