import json
from app.core.session import SessionMemory
from app.core.logger import InterviewLogger
from app.agents.interviewer import InterviewerAgent
from app.agents.observer import ObserverAgent
from app.agents.hiring_manager import HiringManagerAgent
from app.config import client


class InterviewEngine:
    def __init__(self):
        self.memory = SessionMemory()
        self.logger = InterviewLogger()
        self.logger.set_participant_name("Францева Юлия")  # Строго по ТЗ

        self.observer = ObserverAgent(client)
        self.interviewer = InterviewerAgent(client)
        self.hiring_manager = HiringManagerAgent(client)

    def run_interview(self):
        print("=" * 60 + "\n🚀 ЗАПУСК СИСТЕМЫ: ТЕХНИЧЕСКОЕ ИНТЕРВЬЮ\n" + "=" * 60)
        scenario = input("Сценарий №: ")
        intro = input("Представьтесь (Роль, Грейд, Стек): ")

        # Инициализация профиля
        profile = self.interviewer.extract_profile_from_intro(intro)
        self.memory.set_profile(profile)

        last_obs = {"quality": "correct", "reason": "Начало интервью"}
        last_input = intro

        for i in range(1, 11):
            # 1. Сначала генерируем ответ агента
            res = self.interviewer.generate_response(
                last_input, last_obs, self.memory.turns,
                self.memory.candidate_level, self.memory.candidate_role,
                self.memory.stack, self.memory.get_current_difficulty_str()
            )

            # 2. Очищаем текст от системных пометок
            reaction = res.get('reaction', '')
            for bad_word in ["Похвала:", "Строгая:", "Комментарий:", "Реакция:"]:
                reaction = reaction.replace(bad_word, "")

            question = res.get('question', '')
            full_agent_msg = f"{reaction.strip()} {question}".strip()

            print(f"\n🔹 [Ход {i}] 🤖 Agent: {full_agent_msg}")

            # 3. Получаем ввод пользователя
            user_ans = input("👤 You: ")

            # 4. УЛУЧШЕННАЯ ПРОВЕРКА НА ВЫХОД
            # Приводим к нижнему регистру и проверяем наличие ключевых слов
            check_ans = user_ans.lower()
            stop_words = ['стоп', 'exit', 'выход', 'stop', 'завершить']

            if any(word in check_ans for word in stop_words):
                print("\n🛑 Интервью прервано пользователем. Переходим к формированию отчета...")
                break

            # 5. Если не стоп — анализируем ответ Обсервером
            last_obs = self.observer.analyze_answer(
                question, user_ans, self.memory.stack,
                self.memory.candidate_level, self.memory.candidate_role
            )

            # 6. Записываем ход в память и логи
            thoughts = f"[Observer]: {last_obs.get('reason', 'Нет данных')}\n[Interviewer]: {res.get('thought', 'Нет данных')}"
            self.memory.add_turn(question, user_ans, last_obs, res.get('topic'))
            self.logger.log_turn(i, full_agent_msg, user_ans, thoughts)

            # Обновляем входные данные для следующего шага
            last_input = user_ans

        # После выхода из цикла всегда запускаем финал
        self.finish_interview(scenario)

    def finish_interview(self, scenario_num):
        print("\n" + "░" * 60 + "\nФОРМИРОВАНИЕ ОТЧЕТА\n" + "░" * 60)
        data = self.hiring_manager.generate_feedback(self.memory)


        dec = data.get("Decision", {})
        print(f"А. Вердикт (Decision)")
        print(f"   Grade: {dec.get('Grade', 'N/A')}")
        print(f"   Result: {dec.get('Hiring_Recommendation', 'N/A')}")
        print(f"   Confidence: {dec.get('Confidence_Score', 'N/A')}")
        print("-" * 40)


        hs = data.get("Hard_Skills", {})
        print(f"Б. Анализ Hard Skills")
        confirmed = hs.get('Confirmed_Skills', [])
        print(f"   ✅ Confirmed: {', '.join(confirmed) if confirmed else 'Нет подтвержденных данных'}")
        print(f"   ❌ Knowledge Gaps:")
        gaps = hs.get("Knowledge_Gaps", [])
        for gap in gaps:
            if isinstance(gap, dict):
                print(f"      • {gap.get('topic', 'Тема')}: {gap.get('error', 'ошибка в ответе')}")
                print(f"        Правильный ответ: {gap.get('correct_answer', 'Не указан')}")
            else:
                print(f"      • {gap}")
        print("-" * 40)


        ss = data.get("Soft_Skills", {})
        print(f"В. Анализ Soft Skills")
        print(f"   Clarity: {ss.get('Clarity', '0')}/5 | Honesty: {ss.get('Honesty', '0')}/5")
        print(f"   Comments: {ss.get('Comments', 'N/A')}")
        print("-" * 40)


        print(f"Г. Персональный Roadmap")
        roadmap = data.get("Roadmap", [])
        if isinstance(roadmap, list):
            for step in roadmap:
                if isinstance(step, dict):
                    topic = step.get('topic', 'Тема')
                    desc = step.get('description', 'Рекомендуется изучить подробнее')
                    link = step.get('materials', 'Официальная документация')
                    print(f"   📍 {topic}: {desc}")
                    print(f"      🔗 Ресурс: {link}")
                else:
                    print(f"   📍 {step}")
        else:
            print("   📍 Дорожная карта не сформирована.")


        self.logger.save_log(scenario_num, json.dumps(data, ensure_ascii=False))
