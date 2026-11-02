"""
Orchestratore dell'Agente Autonomo AgentGuard.
Coordina NEAR AI Cloud, NEAR Intents e il motore di Policy in un ciclo decisionale sicuro.
"""

from typing import Dict, Any, Optional
import uuid
from agentguard.config import settings
from agentguard.policy import PolicyEngine, PolicyViolation, Receipt
from agentguard.near_ai_client import NearAIClient
from agentguard.intents_client import IntentsClient

class AgentGuard:
    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        ai_client: Optional[NearAIClient] = None,
        intents_client: Optional[IntentsClient] = None
    ):
        self.policy = policy_engine or PolicyEngine(
            max_spend_per_tx_usd=settings.max_spend_per_tx_usd,
            daily_budget_usd=settings.daily_budget_usd,
            max_allowance_near=settings.max_allowance_near
        )
        self.ai = ai_client or NearAIClient()
        self.intents = intents_client or IntentsClient()

    def run_task(self, task_description: str, budget_usd: float) -> Dict[str, Any]:
        """
        Esegue un task completo:
        1. Pianifica tramite NEAR AI Cloud
        2. Valida contro la Policy di sicurezza NEAR
        3. Regola il pagamento tramite NEAR Intents
        4. Emette e restituisce la ricevuta certificata
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # 1. Fase di Ragionamento e Pianificazione (NEAR AI Cloud)
        plan = self.ai.plan_task(task_description, budget_usd)
        
        # 2. Verifica preventiva di Sicurezza (Policy Check)
        allowed, reason = self.policy.evaluate_transaction(
            amount_usd=plan.estimated_cost_usd,
            amount_near=plan.estimated_near,
            receiver_id=plan.target_service,
            method_name=plan.target_method
        )
        
        if not allowed:
            return {
                "success": False,
                "task_id": task_id,
                "error": "PolicyViolation",
                "reason": reason,
                "plan": plan.model_dump(),
                "remaining_allowance_near": self.policy.allowance_near,
                "spent_today_usd": self.policy.spent_today_usd
            }

        # 3. Richiesta Quotazione ed Esecuzione (NEAR Intents)
        quote = self.intents.get_quote(
            token_in="NEAR",
            token_out="USDC",
            amount_in=plan.estimated_near
        )
        
        intent_result = self.intents.execute_intent(
            quote=quote,
            recipient=plan.target_service
        )

        # 4. Registrazione della Spesa e Generazione Scontrino Contabile
        receipt = self.policy.execute_and_record(
            task_id=task_id,
            amount_usd=quote.estimated_cost_usd,
            amount_near=quote.amount_in,
            receiver_id=plan.target_service,
            method_name=plan.target_method,
            mock_tx_hash=intent_result["tx_hash"]
        )

        return {
            "success": True,
            "task_id": task_id,
            "plan_summary": plan.plan_summary,
            "receipt": receipt.model_dump(),
            "remaining_allowance_near": round(self.policy.allowance_near, 3),
            "total_spent_today_usd": round(self.policy.spent_today_usd, 2)
        }
