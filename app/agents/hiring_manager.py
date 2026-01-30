import json
import re
from app.config import MODEL_NAME


class HiringManagerAgent:
    def __init__(self, client):
        self.client = client
        # База знаний со ссылками
        self.resource_library = {
            "SQL": "https://sqlzoo.net/ или https://postgrespro.ru/docs/postgresql/current/tutorial-sql",
            "Python": "https://docs.python.org/3/tutorial/ или https://pythontutor.ru/",
            "Git": "https://git-scm.com/book/ru/v2",
            "Безопасность": "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
            "FastAPI": "https://fastapi.tiangolo.com/tutorial/",
            "Docker": "https://docs.docker.com/get-started/",
            "SOLID": "https://habr.com/ru/articles/348286/"
        }

    def generate_feedback(self, memory) -> dict:
        full_transcript = ""
        for turn in memory.turns:
            full_transcript += (
                f"Topic: {turn.get('topic')}\n"
                f"Q: {turn.get('question')}\n"
                f"A: {turn.get('answer')}\n"
                f"Verdict: {turn['observer_analysis'].get('quality')}\n---\n"
            )

        # Подготавливаем список доступных ресурсов для LLM
        resources_hint = "\n".join([f"- {k}: {v}" for k, v in self.resource_library.items()])

        prompt = f"""
        Ты — Lead Hiring Manager. Проанализируй интервью Юлии Францевой.

        ТРАНСКРИПТ:
        {full_transcript}

        ИСПОЛЬЗУЙ ЭТИ ССЫЛКИ ДЛЯ ROADMAP (если тема подходит):
        {resources_hint}

        ЗАДАЧА: Сгенерируй отчет JSON. 
        В блоке 'Roadmap' для каждой темы ОБЯЗАТЕЛЬНО добавь поле 'materials' с соответствующей ссылкой из списка выше. Если подходящей ссылки нет, дай ссылку на официальную документацию технологии.

        ВЫДАЙ СТРОГО JSON:
        {{
          "Decision": {{
            "Grade": "Junior/Middle/Senior",
            "Hiring_Recommendation": "Hire/No Hire",
            "Confidence_Score": "XX%"
          }},
          "Hard_Skills": {{
            "Confirmed_Skills": ["навык1", "навык2"],
            "Knowledge_Gaps": [
              {{"topic": "тема", "error": "что не так", "correct_answer": "как правильно"}}
            ]
          }},
          "Soft_Skills": {{ "Clarity": 1-5, "Honesty": 1-5, "Comments": "..." }},
          "Roadmap": [
            {{"topic": "Тема", "description": "совет", "materials": "URL"}}
          ]
        }}
        """
        try:
            res = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a professional Hiring Manager. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            text = re.sub(r'```json\s*|```\s*', '', res.choices[0].message.content).strip()
            return json.loads(text)
        except Exception as e:
            return {
                "Decision": {"Grade": "N/A", "Hiring_Recommendation": "Error"},
                "Hard_Skills": {"Confirmed_Skills": [], "Knowledge_Gaps": []},
                "Soft_Skills": {"Clarity": 0, "Honesty": 0, "Comments": str(e)},
                "Roadmap": []
            }