
class OllamaSupervisor:

    def analyze_task(self, task):
        return {
            "task_goal": task.get("goal"),
            "prepared_prompt": f"Architecture context: {task}"
        }

    def evaluate_response(self, response):
        return {
            "quality_score": 0.8,
            "valid": True,
            "actions": []
        }
