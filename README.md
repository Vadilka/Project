# Chatbot LLM + RAG dla programu studiów

## Opis projektu
Inteligentny chatbot do pytań o program studiów, wykorzystujący Large Language Model (LLM) oraz Retrieval-Augmented Generation (RAG). System umożliwia zadawanie pytań w języku polskim i angielskim oraz wyszukiwanie informacji w przesłanych dokumentach i na stronie uczelni.

## Kluczowe funkcje
- Odpowiadanie na pytania o program studiów, przedmioty, egzaminy, wykładowców, regulaminy
- Obsługa języka polskiego i angielskiego
- Wyszukiwanie semantyczne w dokumentach (PDF, CSV, HTML) i na stronie uczelni
- Generowanie odpowiedzi przez LLM (Groq API)
- Przejrzysty web-interfejs (React + Vite)

## Architektura
```
project/
├── backend/    # FastAPI, ChromaDB, przetwarzanie dokumentów, integracja z Groq API
├── frontend/   # React + Vite, interfejs użytkownika (upload, chat)
├── database/   # (rezerwacja pod SQL, obecnie nieużywana)
├── docs/       # Dokumentacja techniczna i architektura
├── tests/      # Testy backendu
```

## Technologie
- **Backend:** Python 3.10+, FastAPI, ChromaDB, sentence-transformers, Groq API
- **Frontend:** React + Vite
- **Wektorowa baza danych:** ChromaDB (lokalnie)
- **LLM:** Groq API (llama3-8b-8192)

## Szybki start
1. **Backend:**
   - Utwórz i aktywuj virtualenv (Python 3.10)
   - `pip install -r requirements.txt`
   - Dodaj plik `.env` z `GROQ_API_KEY=...`
   - `python main.py`
2. **Frontend:**
   - `cd frontend`
   - `npm install && npm run dev`
3. **Przeglądarka:**
   - Otwórz [http://localhost:8000](http://localhost:8000) (API) i [http://localhost:5173](http://localhost:5173) (UI)

## Cechy projektu
- Brak klasycznej bazy SQL — całość wiedzy w ChromaDB (embeddingi)
- LLM działa przez Groq API (nie wymaga GPU)
- Automatyczne scrapowanie strony uczelni
- Przykładowe dokumenty: PDF, CSV, HTML
- Przystosowany do uruchamiania na Windows (PowerShell, venv)
- Instrukcje dla VS Code (wybór interpretera Python)

## Autorzy
Vladyslav Kosolap - 25%
Uladzislau Ishanhaliyeu - 25%
Ivan Dohariev - 25%
Kostiantyn Bukin - 25% 

## Licencja
MIT 