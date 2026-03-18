
class AgentOrchestrator:

    def __init__(self, supervisor):
        self.supervisor = supervisor

    def process_task(self, task):
        context = self.supervisor.analyze_task(task)
        print("Prepared task:", context)
