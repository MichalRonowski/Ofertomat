# Instrukcja obsługi - Ofertomat

## Uruchomienie aplikacji

1. Aktywuj środowisko wirtualne:
   ```
   venv\Scripts\activate
   ```

2. Uruchom aplikację:
   ```
   python main.py
   ```

## Podstawowe funkcje

### 1. Zarządzanie kategoriami

**Nawigacja:** Kliknij "Kategorie" w menu bocznym

- **Dodaj kategorię:** Kliknij przycisk "Dodaj kategorię"
  - Podaj nazwę kategorii (np. "Komputery", "Biuro")
  - Ustaw domyślną marżę w procentach (np. 30 = 30% narzutu)
  
- **Edytuj kategorię:** Kliknij ikonę ołówka przy kategorii
  
- **Usuń kategorię:** Kliknij ikonę kosza (produkty przypisane do tej kategorii zostaną bez kategorii)

### 2. Zarządzanie produktami

**Nawigacja:** Kliknij "Produkty" w menu bocznym

- **Przeglądaj produkty:** Wszystkie produkty wyświetlane są w tabeli
  
- **Wyszukaj produkt:** Użyj pola wyszukiwania u góry (szukaj po nazwie lub kodzie)
  
- **Dodaj produkt ręcznie:**
  - Kliknij "Dodaj produkt"
  - Wypełnij formularz:
    - Kod/Indeks (unikalny identyfikator)
    - Nazwa produktu
    - Jednostka miary (np. szt., kg, m)
    - Cena zakupu netto
    - Stawka VAT (%)
    - Kategoria (opcjonalne)

- **Edytuj produkt:** Kliknij ikonę ołówka
  
- **Usuń produkt:** Kliknij ikonę kosza

**Uwaga:** Data aktualizacji ceny jest automatycznie zapisywana przy każdej zmianie ceny zakupu!

### 3. Import produktów z pliku

**Nawigacja:** Kliknij "Import" w menu bocznym

**Obsługiwane formaty:** CSV, XLS, XLSX

**Wymagane kolumny w pliku:**
- `Nr` / `Indeks` / `Kod` → kod produktu (unikalny)
- `Opis` / `Nazwa` → nazwa produktu

**Opcjonalne kolumny:**
- `Podst. jednostka miary` / `Jednostka` / `JM` → jednostka miary
- `Ostatni koszt bezpośredni` / `Cena zakupu` → cena zakupu netto
- `Tow. grupa księgowa VAT` / `VAT` → stawka VAT (może być: "23%", "23", "0.23")

**Proces importu:**
1. Opcjonalnie wybierz kategorię, do której chcesz przypisać wszystkie importowane produkty
2. Kliknij "Wybierz plik do importu"
3. Wybierz plik CSV/Excel
4. Aplikacja wyświetli wynik:
   - Ile produktów zostało dodanych (nowe)
   - Ile produktów zostało zaktualizowanych (istniejące kody)

**Przykładowy plik CSV znajduje się w:** `przykład_import.csv`

### 4. Tworzenie oferty i generowanie PDF

**Nawigacja:** Kliknij "Nowa Oferta" w menu bocznym

**Proces tworzenia oferty:**

1. **Podaj tytuł oferty** (np. "Oferta dla Klienta X")

2. **Wybierz kategorie:**
   - Zaznacz checkboxy przy kategoriach, które chcesz uwzględnić w ofercie
   - Możesz wybrać jedną lub więcej kategorii

3. **Załaduj produkty:**
   - Kliknij "Załaduj produkty z wybranych kategorii"
   - Wszystkie produkty z wybranych kategorii pojawią się w tabeli

4. **Edytuj ofertę:**
   - **Ilość:** Zmień ilość produktu w polu "Ilość"
   - **Marża:** Dostosuj marżę dla konkretnego produktu (domyślnie ustawiona z kategorii)
   - **Usuń pozycję:** Kliknij ikonę kosza, aby usunąć produkt z oferty
   - Ceny są przeliczane automatycznie po każdej zmianie

5. **Generuj PDF:**
   - Kliknij "Generuj PDF"
   - Plik PDF zostanie zapisany w katalogu aplikacji z nazwą: `Oferta_YYYYMMDD_HHMMSS.pdf`
   - Po wygenerowaniu otworzy się folder z plikiem

**Struktura PDF:**
- Tytuł oferty
- Data
- Produkty pogrupowane według kategorii
- Dla każdego produktu:
  - Nazwa, Ilość, Jednostka miary
  - Cena netto jednostkowa (z marżą)
  - Stawka VAT
  - Cena brutto jednostkowa
  - Wartość netto
  - Wartość brutto
- Podsumowanie dla każdej kategorii
- Suma całkowita netto i brutto

## Kalkulacja cen

**Formuła:**
- Cena sprzedaży netto = Cena zakupu netto × (1 + Marża%)
- Cena brutto = Cena netto × (1 + VAT%)

**Przykład:**
- Cena zakupu: 100 zł netto
- Marża: 30%
- VAT: 23%

Obliczenia:
- Cena sprzedaży netto = 100 × 1.30 = 130 zł
- Cena brutto = 130 × 1.23 = 159.90 zł

## Baza danych

Aplikacja używa lokalnej bazy SQLite (`ofertomat.db`), która jest tworzona automatycznie przy pierwszym uruchomieniu.

**Struktura:**
- `Categories` - kategorie produktów z domyślnymi marżami
- `Products` - produkty z cenami, VAT i przypisaniem do kategorii

**Backup:** Aby zrobić kopię zapasową, skopiuj plik `ofertomat.db`

## Rozwiązywanie problemów

**Aplikacja nie uruchamia się:**
- Upewnij się, że środowisko wirtualne jest aktywne
- Sprawdź czy zainstalowane są wszystkie pakiety: `pip install -r requirements.txt`

**Import nie działa:**
- Sprawdź czy plik ma wymagane kolumny (przynajmniej Nr i Opis/Nazwa)
- Upewnij się, że plik nie jest otwarty w innym programie

**PDF się nie generuje:**
- Sprawdź czy masz uprawnienia zapisu w katalogu aplikacji
- Upewnij się, że oferta zawiera przynajmniej jeden produkt

## Wskazówki

1. **Organizacja:** Najpierw stwórz strukturę kategorii, następnie importuj produkty
2. **Import masowy:** Przy dużej liczbie produktów użyj importu z Excel zamiast ręcznego dodawania
3. **Aktualizacja cen:** Import automatycznie zaktualizuje ceny istniejących produktów (jeśli kod się zgadza)
4. **Marże:** Możesz ustawić domyślne marże na poziomie kategorii i dostosować je indywidualnie w ofercie
5. **Kopia zapasowa:** Regularnie kopiuj plik `ofertomat.db` dla bezpieczeństwa danych
