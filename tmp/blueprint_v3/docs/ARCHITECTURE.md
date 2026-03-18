
# EvoPyramid Hybrid Supervised Agent Mesh

Architecture components:
- External web-based LLM sessions (GPT, Gemini, Claude)
- Local Ollama supervisor
- EvoPyramid orchestration layer

Pipeline:
User Task -> Session Registry -> Ollama Supervisor -> External Worker Agent
-> Evaluation -> Tool Execution -> Pyramid State Update
