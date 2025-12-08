# CHANGELOG - Ofertomat

## Commit: "Fix dialogs for Flet 0.28.3, add input validation, comprehensive testing - all features working"

### 🐛 Naprawione błędy

#### 1. **Dialogi nie wyświetlały się (krytyczny błąd)**
- **Problem**: Wszystkie przyciski (Dodaj, Edytuj, Usuń) wywoływały funkcje, ale dialogi nie pojawiały się na ekranie
- **Przyczyna**: Flet 0.28.3 zmienił API - `page.dialog = dlg` przestało działać
- **Rozwiązanie**: Zmieniono na `page.overlay.append(dlg)` we wszystkich funkcjach dialogowych:
  - `add_category_dialog`
  - `edit_category`
  - `delete_category`
  - `add_product_dialog`
  - `edit_product`
  - `delete_product`
- **Usunięto**: Pomocniczą funkcję `close_dialog()` (niepotrzebną po zmianie)

#### 2. **Blokada bazy danych SQLite**
- **Problem**: Testy kończyły się błędem "database is locked"
- **Przyczyna**: Połączenia do bazy nie były zamykane w przypadku wyjątków (szczególnie IntegrityError przy duplikatach)
- **Rozwiązanie**: 
  - Dodano bloki `finally` we wszystkich funkcjach modyfikujących bazę
  - Dodano timeout 10s dla połączeń SQLite (`sqlite3.connect(path, timeout=10.0)`)
  - Dodano retry mechanism dla `update_category` (3 próby z 0.1s opóźnieniem)
  - Zmieniono `get_categories()` na context manager

#### 3. **Nieprawidłowe usuwanie kategorii**
- **Problem**: `delete_category` usuwało kategorię nawet jeśli miała przypisane produkty
- **Oczekiwane zachowanie**: Powinno zwracać False gdy kategoria zawiera produkty
- **Rozwiązanie**: Dodano sprawdzenie `COUNT(*)` przed usunięciem

#### 4. **Walidacja update_product**
- **Problem**: Próba zaktualizowania produktu z kodem już używanym przez inny produkt kończyła się IntegrityError
- **Rozwiązanie**: Dodano sprawdzenie duplikatu kodu z wykluczeniem aktualnego produktu (`WHERE code = ? AND id != ?`)

#### 5. **Import CSV nie działał z separatorem średnik**
- **Problem**: Pliki CSV z `;` jako separatorem nie były poprawnie parsowane
- **Rozwiązanie**: Dodano inteligentną detekcję separatora - próbuje `;`, potem `,`

#### 6. **Mapowanie kolumn w importerze**
- **Problem**: Brakujące mapowania nazw kolumn (`Cena zakupu netto`, `Vat`)
- **Rozwiązanie**: Rozszerzono `column_mapping` o dodatkowe warianty nazw

#### 7. **Walidacja danych wejściowych w UI**
- **Problem**: ValueError gdy użytkownik wprowadził nieprawidłowe dane (np. "23cc" zamiast "23")
- **Rozwiązanie**: Dodano bloki try/except z komunikatami o błędach:
  - `save_product` (add i edit) - walidacja ceny i VAT
  - `save_category` (add i edit) - walidacja marży

#### 8. **Wersja Flet w requirements.txt**
- **Problem**: `flet==0.24.1` w requirements.txt, ale zainstalowane 0.28.3
- **Rozwiązanie**: Zmieniono na `flet>=0.28.3`

### ✅ Testy end-to-end

Stworzono plik `test_ofertomat.py` z 4 kompletnymi testami:

1. **TEST 1: Operacje na bazie danych**
   - ✓ Dodawanie kategorii (z duplikatami)
   - ✓ Pobieranie kategorii
   - ✓ Aktualizacja kategorii
   - ✓ Dodawanie produktów (z duplikatami)
   - ✓ Pobieranie produktów
   - ✓ Aktualizacja produktu
   - ✓ Usuwanie produktu
   - ✓ Kategoria z produktami nie może być usunięta

2. **TEST 2: Import danych z CSV**
   - ✓ Parsowanie różnych formatów VAT (23%, 0.23, 23)
   - ✓ Mapowanie kolumn (Nr→code, Opis→name, etc.)
   - ✓ Odczyt plików CSV z separatorem średnik

3. **TEST 3: Generowanie PDF**
   - ✓ Kalkulacja cen (zakup + marża + VAT)
   - ✓ Generowanie pliku PDF
   - ✓ Weryfikacja rozmiaru pliku

4. **TEST 4: Scenariusz integracyjny**
   - ✓ Pełny workflow: kategorie → import → zapis do bazy → generowanie PDF

**Wynik: WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE ✅**

### 🧹 Czyszczenie kodu

- Usunięto wszystkie komunikaty DEBUG z `main.py`
- Usunięto przestarzałą funkcję `close_dialog()`
- Dodano poprawną obsługę błędów z komunikatami dla użytkownika

### 📦 Pliki dodane

- `test_ofertomat.py` - kompleksowe testy automatyczne
- `test_dialog.py` - test weryfikacyjny API dialogów Flet 0.28.3

### 🚀 Status aplikacji

**Aplikacja jest w pełni funkcjonalna i przetestowana:**

✅ Kategorie - dodawanie, edycja, usuwanie  
✅ Produkty - dodawanie, edycja, usuwanie  
✅ Import CSV/Excel z inteligentnym mapowaniem kolumn  
✅ Generowanie ofert PDF z kalkulacją cen  
✅ Walidacja danych wejściowych  
✅ Obsługa błędów i komunikaty dla użytkownika  
✅ Baza danych SQLite z prawidłowym zarządzaniem połączeniami  

### 🔗 GitHub

Repozytorium: https://github.com/MichalRonowski/Ofertomat  
Commit: e26d447

---

## Instrukcja uruchomienia

```powershell
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie aplikacji
python main.py

# Uruchomienie testów
python test_ofertomat.py
```

**Wszystkie funkcje działają poprawnie!** 🎉
