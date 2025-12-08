"""
Test end-to-end aplikacji Ofertomat
Testuje wszystkie kluczowe funkcje
"""
import os
import sqlite3
from database import Database
from importer import DataImporter
from pdf_generator import PDFGenerator

def test_database_operations():
    """Test operacji na bazie danych"""
    print("=" * 60)
    print("TEST 1: Operacje na bazie danych")
    print("=" * 60)
    
    # Usuń starą bazę testową jeśli istnieje
    if os.path.exists("test_ofertomat.db"):
        os.remove("test_ofertomat.db")
    
    db = Database("test_ofertomat.db")
    
    # Test dodawania kategorii
    print("\n✓ Test dodawania kategorii...")
    assert db.add_category("Elektronika", 40.0) == True
    assert db.add_category("Narzędzia", 35.0) == True
    assert db.add_category("Materiały", 25.0) == True
    
    # Test duplikatu
    assert db.add_category("Elektronika", 50.0) == False  # duplikat
    print("  ✓ Dodano 3 kategorie, duplikaty zablokowane")
    
    # Test pobierania kategorii
    categories = db.get_categories()
    assert len(categories) >= 3
    print(f"  ✓ Pobrano {len(categories)} kategorii")
    
    # Test aktualizacji kategorii
    cat_id = categories[0]['id']
    assert db.update_category(cat_id, "Elektronika Updated", 45.0) == True
    print("  ✓ Aktualizacja kategorii działa")
    
    # Test produktów
    print("\n✓ Test dodawania produktów...")
    assert db.add_product("PROD001", "Laptop Dell", "szt.", 3000.0, 23.0, cat_id) == True
    assert db.add_product("PROD002", "Myszka Logitech", "szt.", 50.0, 23.0, cat_id) == True
    assert db.add_product("PROD003", "Klawiatura", "szt.", 120.0, 23.0, None) == True
    
    # Test duplikatu produktu
    assert db.add_product("PROD001", "Inny produkt", "szt.", 100.0, 23.0, None) == False
    print("  ✓ Dodano 3 produkty, duplikaty zablokowane")
    
    products = db.get_products()
    assert len(products) >= 3
    print(f"  ✓ Pobrano {len(products)} produktów")
    
    # Test aktualizacji produktu - użyj produktu PROD001
    prod_to_update = next((p for p in products if p['code'] == 'PROD001'), None)
    if not prod_to_update:
        print(f"  ❌ Nie znaleziono PROD001 w produktach: {[p['code'] for p in products]}")
    prod_id = prod_to_update['id']
    assert db.update_product(prod_id, "PROD001", "Laptop Dell XPS", "szt.", 3500.0, 23.0, cat_id) == True
    print("  ✓ Aktualizacja produktu działa")
    
    # Test usuwania produktu
    assert db.delete_product(prod_id) == True
    products_after = db.get_products()
    assert len(products_after) == len(products) - 1
    print("  ✓ Usuwanie produktu działa")
    
    # Test usuwania kategorii z produktami (powinno się nie udać)
    assert db.delete_category(cat_id) == False
    print("  ✓ Kategoria z produktami nie może być usunięta")
    
    # Zamknij wszystkie połączenia
    del db
    import gc
    gc.collect()
    
    # Cleanup
    import time
    time.sleep(0.5)  # Daj czas na zamknięcie połączeń
    try:
        os.remove("test_ofertomat.db")
    except PermissionError:
        print("  ⚠ Nie można usunąć bazy testowej (jeszcze otwarta)")
    print("\n✅ TEST 1 ZAKOŃCZONY POMYŚLNIE\n")
    return True

def test_import_functionality():
    """Test importu z CSV/Excel"""
    print("=" * 60)
    print("TEST 2: Import danych z CSV")
    print("=" * 60)
    
    # Utwórz testowy plik CSV
    test_csv = "test_import.csv"
    with open(test_csv, "w", encoding="utf-8") as f:
        f.write("Nr;Opis;J.m.;Cena zakupu netto;Vat\n")
        f.write("TEST001;Testowy produkt 1;szt.;100.50;23%\n")
        f.write("TEST002;Testowy produkt 2;mb;50.00;0.23\n")
        f.write("TEST003;Testowy produkt 3;kg;25.75;23\n")
    
    print(f"\n✓ Utworzono testowy plik CSV: {test_csv}")
    
    # Test importu
    importer = DataImporter()
    products = importer.import_from_file(test_csv)
    
    assert len(products) == 3
    print(f"  ✓ Zaimportowano {len(products)} produktów")
    
    # Sprawdź poprawność parsowania VAT
    assert products[0]['vat_rate'] == 23.0
    assert products[1]['vat_rate'] == 23.0
    assert products[2]['vat_rate'] == 23.0
    print("  ✓ Parsowanie stawki VAT poprawne (23%, 0.23, 23 → 23.0)")
    
    # Sprawdź mapowanie kolumn
    assert products[0]['code'] == "TEST001"
    assert products[0]['name'] == "Testowy produkt 1"
    assert products[0]['unit'] == "szt."
    # Obsłuż różne formaty liczb (może być string lub float)
    price = float(products[0]['purchase_price_net'])
    assert abs(price - 100.50) < 0.01, f"Expected 100.50 but got {price}"
    print("  ✓ Mapowanie kolumn poprawne")
    
    # Cleanup
    os.remove(test_csv)
    print("\n✅ TEST 2 ZAKOŃCZONY POMYŚLNIE\n")
    return True

def test_pdf_generation():
    """Test generowania PDF"""
    print("=" * 60)
    print("TEST 3: Generowanie PDF")
    print("=" * 60)
    
    # Przygotuj testowe dane
    products = [
        {
            'code': 'PROD001',
            'name': 'Laptop Dell XPS',
            'unit': 'szt.',
            'quantity': 2,
            'purchase_price_net': 3000.0,
            'vat_rate': 23.0,
            'margin': 40.0,
            'category_name': 'Elektronika'
        },
        {
            'code': 'PROD002',
            'name': 'Myszka Logitech',
            'unit': 'szt.',
            'quantity': 5,
            'purchase_price_net': 50.0,
            'vat_rate': 23.0,
            'margin': 45.0,
            'category_name': 'Elektronika'
        },
        {
            'code': 'PROD003',
            'name': 'Klawiatura mechaniczna',
            'unit': 'szt.',
            'quantity': 3,
            'purchase_price_net': 120.0,
            'vat_rate': 23.0,
            'margin': 50.0,
            'category_name': 'Akcesoria'
        },
    ]
    
    print("\n✓ Przygotowano dane testowe (3 produkty, 2 kategorie)")
    
    # Test kalkulacji cen
    pdf_gen = PDFGenerator()
    
    price1 = pdf_gen.calculate_price(3000.0, 40.0, 23.0)
    assert 'net_unit' in price1
    assert 'vat_amount' in price1
    assert 'gross_total' in price1
    assert price1['net_unit'] > 3000.0  # cena sprzedaży wyższa od zakupu
    print(f"  ✓ Kalkulacja ceny: zakup 3000 PLN + 40% marża + 23% VAT = {price1['gross_unit']:.2f} PLN brutto")
    
    # Test generowania PDF
    test_pdf = "test_oferta.pdf"
    offer_data = {
        'title': f"Oferta TEST/001/2024 dla Testowy Klient Sp. z o.o.",
        'date': "2024-01-15",
        'items': products
    }
    success = pdf_gen.generate_offer_pdf(
        offer_data=offer_data,
        output_path=test_pdf
    )
    
    assert success == True
    assert os.path.exists(test_pdf)
    print(f"  ✓ Wygenerowano PDF: {test_pdf}")
    
    # Sprawdź rozmiar pliku
    file_size = os.path.getsize(test_pdf)
    assert file_size > 1000  # PDF powinien mieć przynajmniej 1KB
    print(f"  ✓ Rozmiar pliku: {file_size} bajtów")
    
    # Cleanup
    os.remove(test_pdf)
    print("\n✅ TEST 3 ZAKOŃCZONY POMYŚLNIE\n")
    return True

def test_integration():
    """Test integracyjny - pełny scenariusz"""
    print("=" * 60)
    print("TEST 4: Scenariusz integracyjny (end-to-end)")
    print("=" * 60)
    
    # Usuń starą bazę testową
    test_db = "test_integration.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    db = Database(test_db)
    
    # 1. Dodaj kategorie
    print("\n1. Dodawanie kategorii...")
    db.add_category("Elektronika", 40.0)
    db.add_category("Narzędzia", 35.0)
    categories = db.get_categories()
    cat_elektronika = next((c for c in categories if c['name'] == 'Elektronika'), None)
    print(f"   ✓ Dodano {len(categories)} kategorii")
    
    # 2. Import produktów z CSV
    print("\n2. Import produktów z CSV...")
    test_csv = "test_integration.csv"
    with open(test_csv, "w", encoding="utf-8") as f:
        f.write("Nr;Opis;J.m.;Cena zakupu netto;Vat\n")
        f.write("LAP001;Laptop Dell;szt.;3000;23%\n")
        f.write("MSZ001;Myszka;szt.;50;23%\n")
    
    importer = DataImporter()
    imported = importer.import_from_file(test_csv)
    
    # 3. Zapisz zaimportowane produkty do bazy
    print("\n3. Zapis produktów do bazy...")
    for prod in imported:
        db.add_product(
            prod['code'],
            prod['name'],
            prod['unit'],
            prod['purchase_price_net'],
            prod['vat_rate'],
            cat_elektronika['id'] if cat_elektronika else None
        )
    
    products = db.get_products()
    print(f"   ✓ W bazie {len(products)} produktów")
    
    # 4. Przygotuj ofertę
    print("\n4. Przygotowanie oferty...")
    offer_products = []
    for p in products[:2]:  # Weź pierwsze 2 produkty
        offer_products.append({
            'code': p['code'],
            'name': p['name'],
            'unit': p['unit'],
            'quantity': 2,
            'purchase_price_net': p['purchase_price_net'],
            'vat_rate': p['vat_rate'],
            'margin': 40.0,
            'category_name': 'Elektronika'
        })
    
    # 5. Generuj PDF
    print("\n5. Generowanie oferty PDF...")
    pdf_gen = PDFGenerator()
    test_pdf = "test_integration_oferta.pdf"
    offer_data = {
        'title': "Oferta INT/001/2024 dla Test Integration Client",
        'date': "2024-01-15",
        'items': offer_products
    }
    success = pdf_gen.generate_offer_pdf(
        offer_data=offer_data,
        output_path=test_pdf
    )
    
    assert success == True
    assert os.path.exists(test_pdf)
    print(f"   ✓ PDF wygenerowany: {test_pdf}")
    
    # Cleanup - zamknij bazę
    del db
    import gc
    gc.collect()
    import time
    time.sleep(0.5)
    
    # Cleanup - usuń pliki testowe
    try:
        os.remove(test_db)
        os.remove(test_csv)
        os.remove(test_pdf)
    except PermissionError:
        print("   ⚠ Nie można usunąć plików testowych (jeszcze otwarte)")
    
    print("\n✅ TEST 4 ZAKOŃCZONY POMYŚLNIE\n")
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" OFERTOMAT - TESTY END-TO-END")
    print("=" * 60 + "\n")
    
    try:
        # Uruchom wszystkie testy
        test_database_operations()
        test_import_functionality()
        test_pdf_generation()
        test_integration()
        
        print("=" * 60)
        print("✅ WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE! ✅")
        print("=" * 60)
        print("\nAplikacja jest w pełni funkcjonalna:")
        print("  ✓ Baza danych - CRUD operations")
        print("  ✓ Import CSV/Excel")
        print("  ✓ Generowanie PDF")
        print("  ✓ Integracja wszystkich komponentów")
        print("\nMożesz uruchomić aplikację: python main.py")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
