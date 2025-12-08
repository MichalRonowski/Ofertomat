import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class Database:
    def __init__(self, db_path: str = "ofertomat.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Tworzy połączenie z bazą danych"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inicjalizuje bazę danych z tabelami"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela Categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                default_margin REAL DEFAULT 0.0
            )
        ''')
        
        # Tabela Products
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                unit TEXT DEFAULT 'szt.',
                purchase_price_net REAL DEFAULT 0.0,
                price_update_date TEXT,
                vat_rate REAL DEFAULT 23.0,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES Categories(id)
            )
        ''')
        
        # Dodaj domyślną kategorię jeśli baza jest pusta
        cursor.execute('SELECT COUNT(*) as count FROM Categories')
        if cursor.fetchone()['count'] == 0:
            cursor.execute('INSERT INTO Categories (name, default_margin) VALUES (?, ?)', 
                         ('Bez kategorii', 30.0))
        
        conn.commit()
        conn.close()
    
    # === KATEGORIE ===
    
    def add_category(self, name: str, default_margin: float) -> bool:
        """Dodaje nową kategorię"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Categories (name, default_margin) VALUES (?, ?)', 
                         (name, default_margin))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_categories(self) -> List[Dict]:
        """Pobiera wszystkie kategorie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Categories ORDER BY name')
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def update_category(self, category_id: int, name: str, default_margin: float) -> bool:
        """Aktualizuje kategorię"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE Categories SET name = ?, default_margin = ? WHERE id = ?',
                         (name, default_margin, category_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def delete_category(self, category_id: int) -> bool:
        """Usuwa kategorię (produkty przypisane do niej zostaną bez kategorii)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Products SET category_id = NULL WHERE category_id = ?', 
                     (category_id,))
        cursor.execute('DELETE FROM Categories WHERE id = ?', (category_id,))
        conn.commit()
        conn.close()
        return True
    
    # === PRODUKTY ===
    
    def add_product(self, code: str, name: str, unit: str, purchase_price_net: float, 
                   vat_rate: float, category_id: Optional[int] = None) -> bool:
        """Dodaje nowy produkt"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO Products (code, name, unit, purchase_price_net, price_update_date, vat_rate, category_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, unit, purchase_price_net, now, vat_rate, category_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_product(self, product_id: int, code: str, name: str, unit: str, 
                      purchase_price_net: float, vat_rate: float, category_id: Optional[int]) -> bool:
        """Aktualizuje produkt"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Pobierz starą cenę
            cursor.execute('SELECT purchase_price_net FROM Products WHERE id = ?', (product_id,))
            old_price = cursor.fetchone()['purchase_price_net']
            
            # Jeśli cena się zmieniła, zaktualizuj datę
            if abs(old_price - purchase_price_net) > 0.001:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    UPDATE Products SET code = ?, name = ?, unit = ?, purchase_price_net = ?,
                    price_update_date = ?, vat_rate = ?, category_id = ? WHERE id = ?
                ''', (code, name, unit, purchase_price_net, now, vat_rate, category_id, product_id))
            else:
                cursor.execute('''
                    UPDATE Products SET code = ?, name = ?, unit = ?, purchase_price_net = ?,
                    vat_rate = ?, category_id = ? WHERE id = ?
                ''', (code, name, unit, purchase_price_net, vat_rate, category_id, product_id))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Usuwa produkt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        return True
    
    def get_products(self, category_id: Optional[int] = None) -> List[Dict]:
        """Pobiera produkty (opcjonalnie filtrowane po kategorii)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category_id is not None:
            cursor.execute('''
                SELECT p.*, c.name as category_name, c.default_margin
                FROM Products p
                LEFT JOIN Categories c ON p.category_id = c.id
                WHERE p.category_id = ?
                ORDER BY p.name
            ''', (category_id,))
        else:
            cursor.execute('''
                SELECT p.*, c.name as category_name, c.default_margin
                FROM Products p
                LEFT JOIN Categories c ON p.category_id = c.id
                ORDER BY p.name
            ''')
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Pobiera produkt po ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, c.name as category_name, c.default_margin
            FROM Products p
            LEFT JOIN Categories c ON p.category_id = c.id
            WHERE p.id = ?
        ''', (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def search_products(self, query: str) -> List[Dict]:
        """Wyszukuje produkty po nazwie lub kodzie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        search_pattern = f'%{query}%'
        cursor.execute('''
            SELECT p.*, c.name as category_name, c.default_margin
            FROM Products p
            LEFT JOIN Categories c ON p.category_id = c.id
            WHERE p.name LIKE ? OR p.code LIKE ?
            ORDER BY p.name
        ''', (search_pattern, search_pattern))
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def import_products_batch(self, products: List[Dict]) -> Tuple[int, int]:
        """
        Importuje wiele produktów naraz
        Zwraca (liczba dodanych, liczba zaktualizowanych)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        added = 0
        updated = 0
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for product in products:
            # Sprawdź czy produkt już istnieje
            cursor.execute('SELECT id, purchase_price_net FROM Products WHERE code = ?', 
                         (product['code'],))
            existing = cursor.fetchone()
            
            if existing:
                # Aktualizuj istniejący
                old_price = existing['purchase_price_net']
                if abs(old_price - product['purchase_price_net']) > 0.001:
                    cursor.execute('''
                        UPDATE Products SET name = ?, unit = ?, purchase_price_net = ?,
                        price_update_date = ?, vat_rate = ?, category_id = ?
                        WHERE code = ?
                    ''', (product['name'], product['unit'], product['purchase_price_net'],
                         now, product['vat_rate'], product.get('category_id'), product['code']))
                else:
                    cursor.execute('''
                        UPDATE Products SET name = ?, unit = ?, vat_rate = ?, category_id = ?
                        WHERE code = ?
                    ''', (product['name'], product['unit'], product['vat_rate'], 
                         product.get('category_id'), product['code']))
                updated += 1
            else:
                # Dodaj nowy
                cursor.execute('''
                    INSERT INTO Products (code, name, unit, purchase_price_net, price_update_date, vat_rate, category_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (product['code'], product['name'], product['unit'], 
                     product['purchase_price_net'], now, product['vat_rate'], 
                     product.get('category_id')))
                added += 1
        
        conn.commit()
        conn.close()
        return added, updated
