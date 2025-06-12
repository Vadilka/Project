# Dokumentacja projektu: Chatbot LLM + RAG dla programu studiów

## Architektura systemu

- **Frontend**: React.js (webowy interfejs użytkownika)
- **Backend**: FastAPI (Python)
- **LLM**: Model chmurowy przez Hugging Face Inference API (np. Mistral-7B-Instruct)
- **RAG**: ChromaDB (lokalna baza wektorowa, embeddingi przez sentence-transformers)
- **Baza danych**: (brak klasycznej SQL, całość wiedzy w ChromaDB)

### Schemat działania
1. Użytkownik przesyła dokument (PDF, CSV, HTML) przez /upload
2. Backend wyciąga tekst, dzieli na fragmenty, tworzy embeddingi i zapisuje je w ChromaDB
3. Użytkownik zadaje pytanie przez /chat
4. Backend wykonuje wyszukiwanie semantyczne w bazie wektorowej
5. Najlepsze fragmenty są przekazywane jako kontekst do LLM (chmurowy model)
6. LLM generuje odpowiedź na podstawie kontekstu i pytania

---

## Przykład użycia API

### 1. Upload dokumentu
**POST /upload**
- Plik: syllabus.pdf
- Odpowiedź:
```json
{
  "status": "success",
  "message": "Document processed successfully. 12 chunks added to database."
}
```

### 2. Zapytanie do chatbota
**POST /chat**
```json
{
  "query": "Jakie są przedmioty na 2 semestrze informatyki?",
  "language": "pl"
}
```
- Odpowiedź:
```json
{
  "answer": "Na 2 semestrze informatyki są przedmioty: ...",
  "sources": ["fragment1...", "fragment2..."]
}
```

---

## Funkcjonalne programowanie
W projekcie wykorzystano paradygmat funkcyjny:
- **map**: tworzenie embeddingów dla fragmentów tekstu
- **filter**: filtrowanie niepustych fragmentów
- **funkcje wyższego rzędu**: przekazywanie funkcji jako argumentów (np. do przetwarzania tekstu)

---

## Przegląd istniejących rozwiązań
1. **ChatPDF** – chatbot do PDF-ów (https://www.chatpdf.com/)
2. **Humata** – AI do analizy dokumentów (https://www.humata.ai/)
3. **AskYourPDF** – chatbot do dokumentów (https://askyourpdf.com/)

---

## Możliwości rozwoju
- Dodanie obsługi większej liczby formatów plików
- Integracja z bazą użytkowników
- Lepsza obsługa historii czatu
- Wsparcie dla innych języków

---

## Wskazówki techniczne
- **Windows/PowerShell:** zalecane uruchamianie backendu przez venv (Python 3.10)
- **VS Code:** wybierz interpreter z `backend/venv` dla poprawnej pracy Pylance
- **ChromaDB:** całość wiedzy przechowywana jako embeddingi, nie wymaga SQL
- **LLM:** nie wymaga lokalnego GPU, odpowiedzi generowane przez chmurowy model Hugging Face

---

## Bibliografia
- https://python.langchain.com/
- https://www.trychroma.com/
- https://huggingface.co/
- https://fastapi.tiangolo.com/ 