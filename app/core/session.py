from typing import Dict

class SessionMemory:
    def __init__(self):
        self.turns = []
        self.candidate_level = "Junior"
        self.candidate_role = "Developer"
        self.stack = []
        self.difficulty = 2

    def set_profile(self, profile: Dict):
        self.candidate_level = profile.get("detected_level", "Junior")
        self.candidate_role = profile.get("detected_role", "Developer")
        self.stack = profile.get("stack", [])

    def get_current_difficulty_str(self) -> str:
        return {1: "Easy", 2: "Medium", 3: "Hard"}.get(self.difficulty, "Medium")

    def add_turn(self, question: str, answer: str, observer_analysis: Dict, topic: str):
        q = observer_analysis.get("quality")
        if q == "correct" and self.difficulty < 3: self.difficulty += 1
        elif q in ["wrong", "hallucination"] and self.difficulty > 1: self.difficulty -= 1
        self.turns.append({"question": question, "answer": answer, "observer_analysis": observer_analysis, "topic": topic})