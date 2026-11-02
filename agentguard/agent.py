"""
AgentGuard Autonomous Agent Orchestrator.
Coordinates NEAR AI Cloud, NEAR Intents, and Policy Engine in a secure decision loop.
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
        Executes a complete task cycle:
        1. Plans action via NEAR AI Cloud
        2. Validates plan against NEAR Function Call Key policy
        3. Settles payment via NEAR Intents (1-Click)
        4. Issues and records an immutable cryptographic receipt
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # 1. Reasoning and Planning Phase (NEAR AI Cloud)
        plan = self.ai.plan_task(task_description, budget_usd)
        
        # 2. Pre-flight Security Policy Verification
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

        # 3. Intent Quotation and Execution (NEAR Intents)
        quote = self.intents.get_quote(
            token_in="NEAR",
            token_out="USDC",
            amount_in=plan.estimated_near
        )
        
        intent_result = self.intents.execute_intent(
            quote=quote,
            recipient=plan.target_service
        )

        # 4. Expenditure Recording and Cryptographic Receipt Issuance
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
