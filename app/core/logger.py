import json

class InterviewLogger:
    def __init__(self):
        self.data = {"participant_name": "Францева Юлия", "turns": [], "final_feedback": ""}

    def set_participant_name(self, name: str):
        pass

    def log_turn(self, turn_id: int, agent_msg: str, user_msg: str, thoughts_str: str):
        self.data["turns"].append({
            "turn_id": turn_id,
            "agent_visible_message": agent_msg,
            "user_message": user_msg,
            "internal_thoughts": thoughts_str
        })

    def save_log(self, scenario_num: str, feedback_str: str):
        self.data["final_feedback"] = feedback_str
        with open(f"interview_log_{scenario_num}.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)