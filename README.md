# SupportSphere AI - Backend & Widget Integration Guide

This repository contains the backend for **SupportSphere AI**, a RAG-powered Tier 1 support agent. This guide is designed to help Frontend Developers set up the local environment, ingest test data, and build the client-side chat widget.

## 📋 Prerequisites

*   **Docker Desktop** (for the database)
*   **Python 3.10+**
*   **API Keys** (You will need a valid key for `GOOGLE_API_KEY`)

## 🚀 Quick Start (Local Setup)

Follow these steps to get the API running on your machine.

### 1. Configure Environment
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
**Important:** Update `.env` with your actual API keys:
```ini
GOOGLE_API_KEY=AIza...
```

### 2. Start the Database
Start the PostgreSQL vector database using Docker:
```bash
docker-compose up -d
```

### 3. Install Dependencies
If you have `poetry` installed:
```bash
poetry install
```
Or using standard `pip`:
```bash
pip install -r requirements.txt
```
*(Note: If `requirements.txt` is missing, generate it via `poetry export -f requirements.txt --output requirements.txt`)*

### 4. Ingest Test Data (Crucial!)
The AI starts with an empty brain. You must ingest data so it has something to answer with. Run this command to scrape a Wikipedia page into the `tech_support` knowledge base:

```bash
python -m app.interface.cli.ingest --source "https://en.wikipedia.org/wiki/Artificial_intelligence" --kb "tech_support"
```

### 5. Run the Server
Start the API server:
```bash
python main.py
```
The API will be available at: `http://localhost:8000`

---

## 🔌 API Reference

### **POST** `/api/v1/chat`

This is the primary endpoint for the chat widget.

**Request Headers:**
*   `Content-Type: application/json`

**Request Body:**
```json
{
  "query": "What are the risks of AI?",
  "knowledge_base_id": "tech_support"
}
```

**Response Body (Success - 200 OK):**
```json
{
  "answer": "The risks include technological unemployment and existential threats...",
  "sources": [
    {
      "chunk_id": "uuid-string",
      "source": "https://en.wikipedia.org/wiki/Artificial_intelligence"
    }
  ],
  "status": "success"
}
```

---

## 🛠 Widget Development Guidelines

When building the frontend widget, your code needs to handle three distinct **Status States** returned by the backend.

### 1. Standard Response (`status: "success"`)
*   **Behavior:** Display the `answer` text in a bubble coming from the bot.
*   **Optional:** You can display the `sources` as citations (e.g., "Source: Wikipedia") below the answer for transparency.

### 2. Escalation (`status: "escalated"`)
*   **Trigger:** Occurs when the user is angry or asks for a refund (e.g., "I want a refund", "I am angry").
*   **Behavior:** The backend will return a pre-written message ("I'm escalating this...").
*   **UI Action:** You should visually distinguish this message (e.g., different color, alert icon). Ideally, **display a "Contact Support" button** or a form link immediately after this message.

### 3. No Info Found (`status: "no_content"`)
*   **Trigger:** The AI searched the database but found nothing relevant.
*   **Behavior:** Returns a polite "I don't know" message.
*   **UI Action:** Treat this as a standard message, but perhaps suggest the user rephrase their question.

### 4. Loading States
*   The RAG process (Embedding -> Search -> LLM Generation) can take **2-5 seconds**.
*   **UI Action:** Always show a "Typing..." indicator or skeleton loader after the user sends a message until the response arrives.

---

## 🐛 Troubleshooting

**Error: `429 You exceeded your current quota` (Ingestion)**
*   **Cause:** The Google Gemini API free tier has rate limits.
*   **Fix:** The ingestion script has a built-in delay. If it still fails, wait a minute and try running the script again.

**Error: `Connection refused` (Server)**
*   **Cause:** The Database container isn't running.
*   **Fix:** Run `docker-compose up -d`.

**Error: `CORS Error` in Browser Console**
*   **Cause:** The frontend is running on a different port (e.g., 3000) than the backend (8000).
*   **Fix:** Ask the backend developer to add `CORSMiddleware` to `main.py` allowing your frontend origin.

