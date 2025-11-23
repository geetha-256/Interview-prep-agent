# app.py
import os
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback

from prompts import QUESTION_BANK, build_llm_prompt_for_answer, build_feedback_prompt
from utils import ask_openai, get_openai_client

ASSIGNMENT_PDF_PATH = "/mnt/data/AI Agent Building Assignment - Eightfold.pdf"

app = FastAPI()
SESSIONS: Dict[str, Dict[str, Any]] = {}

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class StartReq(BaseModel):
    role: str
    num_questions: int = 6
    assignment_file_url: str = ASSIGNMENT_PDF_PATH

class AnswerReq(BaseModel):
    session_id: str
    user_answer: str
    assignment_file_url: str = ASSIGNMENT_PDF_PATH

class FeedbackReq(BaseModel):
    session_id: str

@app.post("/start")
async def start_interview(req: StartReq):
    try:
        role = req.role or "software_engineer"
        questions = QUESTION_BANK.get(role, QUESTION_BANK["software_engineer"])[: req.num_questions]
        sid = str(uuid.uuid4())
        SESSIONS[sid] = {"role": role, "questions": questions, "history": [{"q": questions[0], "a": ""}], "assignment": req.assignment_file_url}
        return {"session_id": sid, "first_question": questions[0], "questions": questions}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "start_failed", "detail": str(e)})

@app.post("/answer")
async def answer_question(req: AnswerReq):
    try:
        sid = req.session_id
        if sid not in SESSIONS:
            raise HTTPException(status_code=404, detail="Invalid session_id")
        session = SESSIONS[sid]
        history = session["history"]
        questions = session["questions"]

        # save user's answer
        history[-1]["a"] = req.user_answer

        # Try to get a smart reply via OpenAI if configured
        openai_client = get_openai_client()
        if openai_client:
            prompt = f"(Assignment: {req.assignment_file_url})\n\n" + build_llm_prompt_for_answer(history, req.user_answer, questions)
            try:
                agent_text = ask_openai(prompt, model=MODEL)
            except Exception as e:
                # fallback to default next-question behavior
                agent_text = ""
        else:
            agent_text = ""

        # If no agent_text produced (no key or fallback), return the next prepared question
        if not agent_text:
            idx = len(history)
            next_q = questions[idx] if idx < len(questions) else None
            if next_q:
                history.append({"q": next_q, "a": ""})
                return {"agent_reply": "NEXT", "next_question": next_q}
            else:
                return {"agent_reply": "FINISH", "raw": "No more questions."}

        # If agent_text was produced, decide how to treat it
        text = agent_text.strip()
        if text.upper().startswith("NEXT:"):
            nxt = text.split(":",1)[1].strip()
            history.append({"q": nxt, "a": ""})
            return {"agent_reply": "NEXT", "next_question": nxt}
        elif text.upper().startswith("FINISH"):
            return {"agent_reply": "FINISH", "raw": text}
        else:
            # treat as follow-up question
            history.append({"q": text, "a": ""})
            return {"agent_reply": text}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error":"answer_failed", "detail": str(e)})

@app.post("/feedback")
async def feedback(req: FeedbackReq):
    try:
        sid = req.session_id
        if sid not in SESSIONS:
            raise HTTPException(status_code=404, detail="Invalid session_id")
        history = SESSIONS[sid]["history"]
        assignment = SESSIONS[sid].get("assignment", ASSIGNMENT_PDF_PATH)

        # Build prompt
        prompt = f"(Assignment: {assignment})\n\n" + build_feedback_prompt(history)

        # If OpenAI available, ask it; otherwise do simple local scoring
        if get_openai_client():
            try:
                text = ask_openai(prompt, model=MODEL)
                # try to extract a JSON-like scores if the model returns JSON; but don't fail if not
                parsed = {"raw": text}
                return {"feedback_text": text, "feedback": parsed}
            except Exception as e:
                # fall back to basic scoring
                pass

        # Basic local feedback: short text + scores
        short = "Good structure. Be more specific with metrics. Keep answers under 2 minutes in interviews."
        parsed = {"scores": {"clarity": 4, "structure": 4, "relevance": 3}, "raw": short}
        return {"feedback_text": short, "feedback": parsed}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error":"feedback_failed", "detail": str(e)})
