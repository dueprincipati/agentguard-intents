"""
Client per NEAR AI Cloud (https://api.near.ai/v1).
Gestisce l'inferenza del modello linguistico per il ragionamento e la pianificazione dei task.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
import requests
import json
from agentguard.config import settings

class AgentPlan(BaseModel):
    plan_summary: str
    estimated_cost_usd: float
    estimated_near: float
    target_service: str
    target_method: str
    reasoning: str

class NearAIClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        simulation_mode: Optional[bool] = None
    ):
        self.base_url = base_url or settings.near_ai_base_url
        self.api_key = api_key or settings.near_ai_api_key
        self.model = model or settings.near_ai_model
        self.simulation_mode = simulation_mode if simulation_mode is not None else settings.simulation_mode

    def plan_task(self, task_description: str, budget_limit_usd: float) -> AgentPlan:
        """
        Invia il task al modello su NEAR AI Cloud per ottenere un piano d'azione strutturato.
        """
        # Se siamo in simulazione o la chiave è mock, forniamo una risposta strutturata e deterministica
        if self.simulation_mode or self.api_key == "mock-key":
            return AgentPlan(
                plan_summary=f"Esecuzione controllata del task: '{task_description}'",
                estimated_cost_usd=min(1.50, budget_limit_usd),
                estimated_near=0.395,  # ~1.50 USD al tasso di ~3.80 USD/NEAR
                target_service="intents.near",
                target_method="execute_intent",
                reasoning=(
                    "Il task richiede l'acquisto di un servizio o micro-pagamento cross-chain. "
                    "Verrà utilizzato il contratto intents.near per saldare la spesa rimanendo "
                    "entro il budget massimo autorizzato."
                )
            )

        # Chiamata REST reale a NEAR AI Cloud (OpenAI-compatible chat completions)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            "Sei un agente autonomo su NEAR Protocol. "
            "Rispondi SOLO in formato JSON valido con i campi: "
            "plan_summary (str), estimated_cost_usd (float), estimated_near (float), "
            "target_service (str), target_method (str), reasoning (str)."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Task: {task_description}. Budget max: ${budget_limit_usd}"}
            ],
            "temperature": 0.2
        }

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return AgentPlan(**parsed)
        except Exception as e:
            # Fallback di sicurezza in caso di temporanea indisponibilità dell'endpoint remoto
            return AgentPlan(
                plan_summary=f"Piano fallback per: {task_description}",
                estimated_cost_usd=1.00,
                estimated_near=0.263,
                target_service="intents.near",
                target_method="execute_intent",
                reasoning=f"Generato tramite fallback locale di sicurezza: {str(e)}"
            )
