# Ofertomat

Lokalna aplikacja desktopowa do zarządzania produktami i generowania ofert sprzedażowych.

## Funkcjonalności
- Import produktów z plików CSV/Excel
- Zarządzanie kategoriami i marżami
- Tworzenie ofert z automatyczną kalkulacją cen
- Generowanie raportów PDF

## Instalacja

1. Stwórz środowisko wirtualne:
```bash
python -m venv venv
```

2. Aktywuj środowisko:
```bash
# Windows
venv\Scripts\activate
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
python main.py
```

## Technologie
- Python 3.x
- Flet (UI Framework)
- SQLite (Baza danych)
- Pandas (Import danych)
- ReportLab (Generowanie PDF)
