import json
import re
from typing import Dict
from app.config import MODEL_NAME

class ObserverAgent:
    def __init__(self, client):
        self.client = client

    def analyze_answer(self, question: str, answer: str, stack: list, level: str, role: str) -> Dict:
        prompt = f"""
Ты — Technical Observer. Твоя единственная цель — выявить бред (галлюцинации).
Вопрос: "{question}"
Ответ кандидата: "{answer}"

КЛАССИФИКАЦИЯ (quality):
1. hallucination: если кандидат пишет про магию, телепатию, квантовые кристаллы или вымышленные технологии.
2. meta_question: если кандидат спрашивает "что такое SQL" (когда сам его заявлял) или задает вопросы тебе.
3. correct: технически верный ответ.
4. wrong: техническая ошибка.

ВЫДАЙ JSON:
{{
    "quality": "hallucination/meta_question/correct/wrong",
    "reason": "Техническое обоснование твоего вердикта",
    "internal_thought": "Твое скрытое мнение для логгера"
}}
"""
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.1
        )
        text = re.sub(r'```json\s*|```\s*', '', response.choices[0].message.content).strip()
        return json.loads(text)