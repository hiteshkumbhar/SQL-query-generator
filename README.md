# Natural Language → SQL (Flask + HTML/CSS)

A lightweight, zero-dependency frontend Text-to-SQL web application powered by **Python Flask** and **Google Gemini API**.

---

## 🚀 How to Run on Your Laptop (Localhost)

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- A **Gemini API Key** (Get free from [Google AI Studio](https://aistudio.google.com/app/apikey)).

---

### 2. Quick Setup

1. **Extract the ZIP file** to a folder on your computer.
2. Open a terminal / command prompt inside that folder.
3. (Optional but recommended) **Create a virtual environment**:
   ```bash
   # On macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows (cmd/powershell):
   python -m venv venv
   venv\Scripts\activate
   ```
4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Configure Your Gemini API Key

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` in any text editor and paste your API key:
```env
GEMINI_API_KEY=AIzaSy...your_actual_key_here...
```

---

### 4. Run the Application

```bash
python run.py
```

Open your browser and navigate to:
```
http://localhost:3000
```
(Or the port specified in your `.env`, default is `3000`).

---

## 📁 Project Structure

```
├── run.py                 # Application entry point
├── config.py              # Configuration settings & environment variables
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── app/
│   ├── __init__.py        # Flask App factory
│   ├── prompts/           # Gemini prompt definitions & rules
│   ├── routes/            # REST API endpoints & page routes
│   ├── services/          # Gemini API integration & SQL orchestrator
│   ├── utils/             # Helpers & rate limiter
│   └── validators/        # Request payload validators
├── static/
│   └── css/
│       └── style.css      # Pure CSS3 styling & animations
└── templates/
    └── index.html         # Pure HTML5 interface & client-side controller
```

---

## ✨ Features
- **All SQL Query Support**: DQL (`SELECT`, CTEs), DML (`INSERT`, `UPDATE`, `DELETE`), and DDL (`CREATE TABLE`, `ALTER TABLE`, `DROP`, `TRUNCATE`).
- **Multiple Dialects**: PostgreSQL, MySQL, SQLite, BigQuery, Snowflake, and SQL Server.
- **Pure HTML & CSS**: No Node.js, no React, no Tailwind, zero frontend build tools. Fast and lightweight.
- **Local History**: Stored directly in your browser.
- **Copy & Download**: Export queries as `.sql` files with 1 click.
