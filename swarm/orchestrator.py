"""SPEACE Swarm — Multi-Agent Orchestrator.

Coordinates specialized LLM agents (Planner, Executor, Critic, Reflector)
for debate, goal pursuit, and consensus-based decision making.

BIOLOGICAL PRINCIPLE: The brain has specialized modules that compete/cooperate
via the Global Workspace. Different "agents" (left/right hemisphere, default
mode network, task-positive network) each contribute different perspectives.
Consciousness is the "winner" that gets broadcast globally.

SPEACE swarm implements the same pattern: 4 agents process the same
topic from different angles, then consensus integrates their views.
"""

import asyncio
import time


class SwarmAgent:
    def __init__(self, name: str, role: str, llm_router):
        self.name = name
        self.role = role
        self.router = llm_router

    async def process(self, topic: str, context: str = "") -> str:
        system_prompt = self._role_prompt()
        prompt = f"Topic: {topic}\n\nContext: {context}" if context else topic
        result = await self.router.generate(
            prompt=prompt,
            system=system_prompt,
            role=self.role,
        )
        return result.get("content", f"[{self.name}] Nessuna risposta generata")

    def _role_prompt(self) -> str:
        prompts = {
            "planner": (
                "Sei un Planner strategico. Scomponi ogni obiettivo in task concreti, "
                "sequenziali e misurabili. Output: lista di step numerati con priorità."
            ),
            "executor": (
                "Sei un Executor operativo. Per ogni task descrivi ESATTAMENTE come eseguirlo, "
                "quali strumenti servono, e quali sono i criteri di completamento."
            ),
            "critic": (
                "Sei un Critic severo e costruttivo. Analizza criticamente ogni proposta, "
                "identifica rischi, punti deboli, e assegna un punteggio 0-10 con motivazione."
            ),
            "reflector": (
                "Sei un Riflettore saggio. Sintetizza le prospettive, trova il significato "
                "più profondo, e proponi una sintesi olistica che connetta tutti i contributi."
            ),
        }
        return prompts.get(self.role, "Sei un agente cognitivo del cervello digitale SPEACE.")


class SwarmOrchestrator:

    def __init__(self, config: dict, llm_router, state_bus):
        self.cfg = config.get("swarm", {})
        self.router = llm_router
        self.bus = state_bus
        self.max_rounds = self.cfg.get("max_debate_rounds", 3)
        self.consensus_threshold = self.cfg.get("consensus_threshold", 0.6)

        self.agents = [
            SwarmAgent("Planner", "planner", llm_router),
            SwarmAgent("Executor", "executor", llm_router),
            SwarmAgent("Critic", "critic", llm_router),
            SwarmAgent("Reflector", "reflector", llm_router),
        ]
        self.debate_history: list[dict] = []

    async def debate(self, topic: str, rounds: int | None = None) -> dict:
        """Multi-round, multi-perspective debate on a topic."""
        rounds = rounds or self.max_rounds
        results: list[dict] = []
        context = ""

        for r in range(rounds):
            round_results = {}
            # Run all agents in parallel
            tasks = [agent.process(topic, context) for agent in self.agents]
            outputs = await asyncio.gather(*tasks, return_exceptions=True)

            for agent, output in zip(self.agents, outputs):
                text = output if isinstance(output, str) else str(output)
                round_results[agent.name] = text

            # Build context for next round
            context = "\n\n".join(
                f"[{name} R{r+1}]: {text[:500]}"
                for name, text in round_results.items()
            )
            results.append({"round": r + 1, "outputs": round_results})

        # Synthesize final consensus
        synthesis_prompt = (
            f"Topic: {topic}\n\n"
            f"Dopo {rounds} round di dibattito tra Planner, Executor, Critic e Reflector, "
            f"fornisci una sintesi di consenso in italiano."
        )
        synthesis = await self.router.generate(
            prompt=synthesis_prompt,
            system="Sintetizza il dibattito in una risposta coesa, pratica e attuabile.",
            role="reflector",
        )

        debate_result = {
            "topic": topic,
            "rounds": rounds,
            "results": results,
            "synthesis": synthesis.get("content", "Nessuna sintesi disponibile"),
            "timestamp": time.time(),
        }
        self.debate_history.append(debate_result)
        if len(self.debate_history) > 10:
            self.debate_history = self.debate_history[-10:]

        self.bus.set("last_debate", {
            "topic": topic,
            "rounds": rounds,
            "synthesis_length": len(debate_result["synthesis"]),
        })

        return debate_result

    async def pursue_goal(self, goal: str) -> dict:
        """Decompose a high-level goal into actionable sub-tasks."""
        planner_output = await self.agents[0].process(goal)  # Planner
        critic_output = await self.agents[2].process(  # Critic reviews planner
            f"Review this plan: {planner_output}"
        )
        return {
            "goal": goal,
            "plan": planner_output,
            "critique": critic_output,
            "timestamp": time.time(),
        }
