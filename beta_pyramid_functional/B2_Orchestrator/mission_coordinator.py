from typing import List, Dict, Any, Optional
from beta_pyramid_functional.B3_SessionRegistry.session_models import AgentSession, Provider
from beta_pyramid_functional.B2_Orchestrator.llm_orchestrator import AgentOrchestrator
from beta_pyramid_functional.B2_Orchestrator.mission_registry import MissionRegistry
from beta_pyramid_functional.B2_Orchestrator.mission_models import Mission, MissionTask, MissionStatus

class MissionCoordinator:
    """
    Strategic Orchestrator for Multi-Agent Swarms.
    Decomposes Z17 objectives into Z5-Z16 tasks.
    """
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.registry: Optional[MissionRegistry] = None

    async def _ensure_registry(self):
        if not self.registry:
            self.registry = await MissionRegistry.get_instance()

    async def create_mission(self, title: str, objective: str) -> Mission:
        """Phase 1: Decompose objective into a strategic plan using LLM Architect."""
        await self._ensure_registry()
        
        mission = Mission(title=title, objective=objective)
        print(f"[MISSION] Planning strategic decomposition for: {title}")
        
        # Dynamically plan the mission using the Architect persona
        plan = await self.orchestrator.plan_mission(objective)
        
        mission.tasks = []
        for task_def in plan:
            mission.tasks.append(MissionTask(
                assigned_role=task_def.get("role", "Generalist"),
                z_level=task_def.get("z_level", 5),
                intent=task_def.get("intent", objective)
            ))
        
        mission.status = MissionStatus.ACTIVE
        await self.registry.save_mission(mission)
        print(f"[MISSION] Strategic Plan Created: {len(mission.tasks)} tasks assigned.")
        return mission

    async def execute_mission(self, mission_id: str):
        """Phase 2: Dispatch tasks to the swarm."""
        await self._ensure_registry()
        mission = self.registry.get_mission(mission_id)
        if not mission:
            return
        
        print(f"[MISSION] Starting: {mission.title} ({mission.id})")
        
        # Currently executing tasks sequentially for dependency management, 
        # but can be parallelized if no dependencies exist.
        for task in mission.tasks:
            print(f"[MISSION] Dispatching Task: {task.assigned_role} (Z{task.z_level}) -> {task.intent}")
            
            # Create a session for the specific agent
            session = AgentSession(
                node_id=f"mission-{mission.id}-{task.assigned_role.lower()}",
                node_z=task.z_level,
                task_title=f"Mission Task: {mission.title}",
                provider=Provider.OLLAMA, # Default to local for swarm tasks
                task_context=f"OBJECTIVE: {mission.objective} | TASK INTENT: {task.intent}"
            )
            
            # Add the task intent as a message
            session.add_user_message(f"Execute: {task.intent}")
            
            # Simulate agent execution via orchestrator
            # In full PEAR integration, we would call PEARAgent.perceive/evolve/act
            response = await self.orchestrator.get_response(session)
            
            task.status = "completed"
            task.result_ref = f"sk_memory_{task.task_id}" # Simplified memory ref
            print(f"[MISSION] Task Completed by {task.assigned_role}.")

        mission.status = MissionStatus.COMPLETED
        await self.registry.save_mission(mission)
        print(f"[MISSION] Completed: {mission.title}")
        return mission
