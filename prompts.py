# prompts.py
QUESTION_BANK = {
    "software_engineer": [
        "Tell me about a time you solved a difficult bug.",
        "Describe a time you took initiative.",
        "Explain a situation where you exceeded expectations.",
        "Tell me about a time you handled conflict in a team.",
        "Describe a mistake you made and what you learned.",
        "Tell me about a time you improved a system or process."
    ],
    "sales": [
        "Tell me about a time you closed a difficult sale.",
        "How do you handle rejection from customers?",
        "Describe a time you exceeded your sales target."
    ],
    "retail_associate": [
        "Tell me about a time you helped a difficult customer.",
        "How do you prioritize tasks on a busy day?",
        "Describe a time you improved store operations."
    ]
}

def build_llm_prompt_for_answer(history, user_answer, questions):
    """
    Build a short prompt for the LLM: include previous Q/A and the user's new answer.
    """
    conv = ""
    for i, h in enumerate(history):
        conv += f"Q{i+1}: {h.get('q','')}\nA{i+1}: {h.get('a','')}\n"
    conv += f"\nUser's latest answer: {user_answer}\n\n"
    conv += "As an interview coach, respond either with:\n"
    conv += "NEXT: <next question>\nOR\n"
    conv += "FINISH: <closing message>\nOR\n"
    conv += "<a short follow-up question>\n"
    return conv

def build_feedback_prompt(history):
    conv = ""
    for i, h in enumerate(history):
        conv += f"Q{i+1}: {h.get('q','')}\nA{i+1}: {h.get('a','')}\n"
    conv += "\nProvide a short feedback (3-5 sentences) and a simple JSON with numeric scores (clarity, structure, relevance) 1-5.\n"
    return conv
