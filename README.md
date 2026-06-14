# AI Code Quality Assistant

Asystent AI do analizy jakości kodu z wykorzystaniem Google Gemini API.

## 📋 Funkcjonalności

- ✅ Analiza kodu w wielu językach programowania
- ✅ Ocena jakości kodu (1-10)
- ✅ Identyfikacja problemów bezpieczeństwa
- ✅ Sugestie ulepszeń
- ✅ Automatyczne poprawianie kodu
- ✅ Usuwanie komentarzy z kodu
- ✅ Kopiowanie do schowka

## 🏗️ Struktura Projektu

```
AsystentAI/
├── app/                          # Główny pakiet aplikacji
│   ├── __init__.py              # Inicjalizacja Flask app
│   ├── routes/                  # Routing aplikacji
│   │   ├── __init__.py
│   │   └── analysis.py          # Endpoint /api/analyze
│   ├── services/                # Logika biznesowa
│   │   ├── __init__.py
│   │   └── gemini_service.py    # Integracja z Gemini API
│   ├── templates/               # Szablony HTML
│   │   └── index.html
│   └── static/                  # Pliki statyczne
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── script.js
│
├── config.py                     # Konfiguracja aplikacji
├── run.py                        # Punkt wejścia (main)
├── requirements.txt              # Zależności Python
├── .env.example                 # Szablon zmiennych środowiskowych
└── README.md                    # Ten plik
```

## 🚀 Instalacja

### 1. Klonowanie repozytorium
```bash
git clone <repo-url>
cd AsystentAI
```

### 2. Tworzenie wirtualnego środowiska
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# lub
venv\Scripts\activate  # Windows
```

### 3. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 4. Konfiguracja zmiennych środowiskowych
```bash
cp .env.example .env
# Edytuj .env i dodaj klucz API od Google Gemini
```

### 5. Uruchomienie
```bash
python run.py
```

Aplikacja będzie dostępna na http://127.0.0.1:5000

## 🔑 Zmienne Środowiskowe

Utwórz plik `.env`:

```
GEMINI_API_KEY=your-api-key-here
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

## 📚 API Endpoints

### GET /
Zwraca główną stronę aplikacji.

### POST /api/analyze
Analizuje kod i zwraca ocenę.

**Request:**
```json
{
    "code": "python code here...",
    "language": "python"
}
```

**Response:**
```json
{
    "quality_score": 9,
    "issues": ["issue 1"],
    "suggestions": ["suggestion 1"],
    "corrected_code": "improved code here..."
}
```

## 🛠️ Technologia

- **Backend:** Flask (Python 3.9+)
- **AI:** Google Gemini API
- **Frontend:** HTML, CSS, JavaScript
- **Password Hashing:** bcrypt

## 📝 Ocena Kodu

Asystent ocenia kod na skali 1-10:

- **1-2/10:** Krytyczne błędy bezpieczeństwa
- **3-4/10:** Wiele poważnych problemów
- **5-7/10:** Kod funkcjonalny ale z problemami
- **8/10:** Dobry kod, bezpieczny
- **9-10/10:** Doskonały kod, gotowy do produkcji

## ⚠️ Notatki

- Limit darmowego planu: 5 żądań na minutę
- Niski limit? Upgrade do planu paid na Google AI Studio
- Python 3.9+ wymagany

## 👨‍💼 Autor

[Katarzyna]

## 📄 Licencja

MIT

