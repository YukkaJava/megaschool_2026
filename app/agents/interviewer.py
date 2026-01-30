import json
import re
from typing import Dict, List
from app.config import MODEL_NAME


class InterviewerAgent:
    def __init__(self, client):
        self.client = client

    def generate_response(self, candidate_input: str, observer_feedback: Dict, session_history: List,
                          level: str, role: str, stack: List[str], difficulty: str) -> Dict:
        q_type = observer_feedback.get("quality", "correct")
        reason = observer_feedback.get("reason", "")

        prompt = f"""
Ты — Senior IT Interviewer. 
Кандидат сказал: "{candidate_input}"
Вердикт Observer: {q_type} ({reason})

ПРАВИЛА:
1. Если 'hallucination' — СТРОГО разоблачи бред. Скажи, что магии в IT нет.
2. Если 'meta_question' — Ответь, что ты здесь, чтобы спрашивать, а не отвечать. Вернись к теме.
3. В поле "reaction" пиши ТОЛЬКО живую речь. Никаких слов "Похвала", "Строгая", "Комментарий".

ВЫДАЙ JSON:
{{
  "thought": "Внутренний план",
  "reaction": "Твоя живая реплика",
  "question": "Твой следующий вопрос",
  "topic": "Тема"
}}
"""
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": "Speak Russian. Output JSON only."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        text = re.sub(r'```json\s*|```\s*', '', response.choices[0].message.content).strip()
        return json.loads(text)

    def extract_profile_from_intro(self, intro: str) -> Dict:
        prompt = f"Extract JSON (detected_name, detected_level, detected_role, stack) from: {intro}"
        res = self.client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        return json.loads(re.sub(r'```json\s*|```\s*', '', res.choices[0].message.content).strip())