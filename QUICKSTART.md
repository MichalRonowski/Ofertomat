# Quick Start - Ofertomat

## 🚀 Pierwsze kroki (5 minut)

### 1. Uruchom aplikację
Kliknij dwukrotnie na: **uruchom.bat**

Lub w terminalu:
```bash
venv\Scripts\activate
python main.py
```

### 2. Dodaj kategorie

1. W menu bocznym kliknij **"Kategorie"**
2. Kliknij **"Dodaj kategorię"**
3. Stwórz pierwsze kategorie, np.:
   - Nazwa: "Komputery" → Marża: 25%
   - Nazwa: "Akcesoria" → Marża: 40%
   - Nazwa: "Biuro" → Marża: 35%

### 3. Importuj produkty z pliku testowego

1. W menu bocznym kliknij **"Import"**
2. Z dropdowna wybierz kategorię "Komputery"
3. Kliknij **"Wybierz plik do importu"**
4. Wybierz plik: **przykład_import.csv**
5. Gotowe! Aplikacja zaimportuje 10 produktów

### 4. Stwórz pierwszą ofertę

1. W menu bocznym kliknij **"Nowa Oferta"**
2. W polu "Tytuł oferty" wpisz: "Oferta testowa"
3. Zaznacz checkbox przy kategorii "Komputery"
4. Kliknij **"Załaduj produkty z wybranych kategorii"**
5. W tabeli możesz:
   - Zmienić ilość produktów
   - Dostosować marżę dla konkretnych pozycji
   - Usunąć niepotrzebne produkty
6. Kliknij **"Generuj PDF"**
7. Gotowe! PDF zostanie zapisany w folderze aplikacji

### 5. Zarządzaj produktami

1. W menu bocznym kliknij **"Produkty"**
2. Możesz:
   - Wyszukiwać produkty (pole wyszukiwania u góry)
   - Edytować ceny i przypisania do kategorii
   - Dodawać nowe produkty ręcznie
   - Usuwać produkty

## 📊 Przykładowy przepływ pracy

```
1. Kategorie → Dodaj kategorie produktowe
2. Import → Zaimportuj bazę produktów z Excel/CSV
3. Produkty → Sprawdź i popraw dane jeśli potrzeba
4. Nowa Oferta → Stwórz ofertę i wygeneruj PDF
```

## 💡 Wskazówki

- **Import aktualizuje ceny** - jeśli importujesz plik z tym samym kodem produktu, cena zostanie zaktualizowana
- **Marże na poziomach** - ustaw domyślne marże w kategoriach, a potem dostosuj je w ofercie
- **Grupowanie w PDF** - oferta PDF grupuje produkty według kategorii automatycznie
- **Backup** - plik `ofertomat.db` zawiera całą bazę danych

## ❓ Potrzebujesz pomocy?

Zajrzyj do pliku **INSTRUKCJA.md** dla szczegółowej dokumentacji.
