Interview Practice Agent

This project is a simple end-to-end Interview Practice Agent built using Streamlit (frontend) and FastAPI (backend). The agent asks interview questions, accepts user answers, and provides AI-generated or fallback feedback. The system also references the assignment PDF provided with the project.

Assignment File Path:
/mnt/data/AI Agent Building Assignment - Eightfold.pdf

Features

Start an interview session for a selected role.

Dynamic question flow.

AI-based answer evaluation using OpenAI GPT models (optional).

Automatic fallback mode if API key is missing or quota is exceeded.

Final feedback summary with score visualization using Plotly.

Simple layout with all files stored in the main folder.

Beginner-friendly and easy to run.

Project Structure

All files are stored in a single directory for simplicity.

app.py
streamlit_app.py
prompts.py
utils.py
requirements.txt
README.md
.gitignore

Setup Instructions (Windows + VS Code)

Create a virtual environment:
python -m venv .venv

Activate the virtual environment:
..venv\Scripts\Activate.ps1

Install all dependencies:
pip install -r requirements.txt

Optional: Configure OpenAI API Key

If you want real AI responses, set your API key in the backend terminal:

$env:OPENAI_API_KEY = "your_api_key_here"

If the key is not set or quota is exceeded, the app automatically switches to fallback mode.

Running the Backend (FastAPI)

In one terminal:

uvicorn app:app --port 8000

Backend runs at:
http://127.0.0.1:8000

Keep this terminal running.

Running the Frontend (Streamlit)

Open a second terminal, activate the virtual environment again, then run:

streamlit run streamlit_app.py

Frontend runs at:
http://localhost:8501

Architecture Overview

Streamlit Frontend

Handles user interface, forms, questions, and results.

Communicates with backend via HTTP POST requests.

Displays the final summary and Plotly charts.

FastAPI Backend

Manages interview sessions.

Stores and updates Q&A history.

Generates next interview questions.

Generates final feedback (AI-powered or fallback).

Handles errors and avoids failures.

LLM Integration

Uses the OpenAI Python client (version 1.x).

If API fails, missing key, or insufficient quota, the system falls back to safe text scoring.

Assignment File Use

The assignment file located at:
/mnt/data/AI Agent Building Assignment - Eightfold.pdf
is included in prompts for contextual relevance.

Design Decisions

Single-folder layout for simplicity.

No database; sessions stored in memory.

Minimalistic but scalable architecture.

Automatic fallback mode ensures the system never breaks.

Code structured for easy learning and modification.

Dependencies

The required libraries are listed in requirements.txt:

fastapi
uvicorn
streamlit
requests
openai
pydantic
plotly
pandas

How to Publish the Repository

Create a new public GitHub repository.

Push your project with the following commands:

git init
git add .
git commit -m "Initial commit - interview practice agent"
git branch -M main
git remote add origin https://github.com/your-username/your-repo.git

git push -u origin main

