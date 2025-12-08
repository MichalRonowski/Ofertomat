@echo off
echo ====================================
echo       OFERTOMAT - Uruchamianie
echo ====================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo [BŁĄD] Nie znaleziono środowiska wirtualnego!
    echo Uruchom najpierw: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Uruchamianie aplikacji...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [BŁĄD] Wystąpił problem podczas uruchamiania aplikacji.
    pause
)
