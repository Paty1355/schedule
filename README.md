# Plan - Instrukcja instalacji i uruchomienia

## Instalacja

### 1. Instalacja bibliotek Python

Zainstaluj wymagane biblioteki z pliku `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Instalacja PostgreSQL

Jeśli nie masz zainstalowanego PostgreSQL, pobierz go ze strony:

**https://www.postgresql.org/download/**

Wybierz wersję odpowiednią dla Twojego systemu operacyjnego i postępuj zgodnie z instrukcjami instalatora.

### 3. Konfiguracja zmiennych środowiskowych

Utwórz plik `.env` w głównym katalogu projektu z następującą zawartością:

```
DB_NAME=schedule
DB_USER=postgres
DB_PASSWORD=tutaj_haslo
DB_HOST=localhost
DB_PORT=5432
```

**Uwaga:** Zastąp `tutaj_haslo` swoim rzeczywistym hasłem do PostgreSQL.

### 4. Uruchomienie bazy danych PostgreSQL

Uruchom bazę danych poleceniem:

```bash
psql -U postgres
```

#### Rozwiązywanie problemów

Jeśli system nie rozpoznaje polecenia `psql`, musisz dodać PostgreSQL do zmiennych środowiskowych PATH:

1. Otwórz **Ustawienia systemu** → **Zmienne środowiskowe**
2. Znajdź zmienną **Path** i kliknij **Edytuj**
3. Dodaj ścieżkę do katalogu `bin` PostgreSQL, np.:
   ```
   C:\Program Files\PostgreSQL\16\bin
   ```
4. Zapisz zmiany i uruchom ponownie terminal

### 5. Uruchomienie aplikacji

Uruchom aplikację Streamlit poleceniem:

```bash
streamlit run plan.py
```

Aplikacja powinna otworzyć się automatycznie w przeglądarce. Jeśli nie, przejdź do adresu wyświetlonego w terminalu (zazwyczaj `http://localhost:8501`).

