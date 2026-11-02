"""
Policy & Security Engine for AgentGuard.
Models the constraints of NEAR Function Call Keys, preventing unauthorized transactions.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
import uuid

class Receipt(BaseModel):
    """Cryptographic and accounting receipt of an expenditure executed by the agent."""
    receipt_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    task_id: str
    target_service: str
    amount_usd: float
    amount_near: float
    tx_hash: str
    status: str = "SETTLED"

class PolicyViolation(Exception):
    """Raised when an agent attempts to violate spending or permission policies."""
    pass

class PolicyEngine:
    def __init__(
        self,
        max_spend_per_tx_usd: float = 2.00,
        daily_budget_usd: float = 5.00,
        max_allowance_near: float = 2.00,
        allowed_receivers: Optional[List[str]] = None,
        allowed_methods: Optional[List[str]] = None
    ):
        self.max_spend_per_tx_usd = max_spend_per_tx_usd
        self.daily_budget_usd = daily_budget_usd
        self.allowance_near = max_allowance_near
        self.spent_today_usd = 0.0
        
        # Whitelist of authorized receivers and methods (matching NEAR Function Call Keys)
        self.allowed_receivers = allowed_receivers or ["intents.near", "v1.agent-market.near", "defuse.near"]
        self.allowed_methods = allowed_methods or ["execute_intent", "request_task", "settle_payment"]
        
        # Audit log of receipts
        self.receipts: List[Receipt] = []

    def evaluate_transaction(
        self,
        amount_usd: float,
        amount_near: float,
        receiver_id: str,
        method_name: str
    ) -> Tuple[bool, str]:
        """
        Evaluates whether a proposed transaction adheres to all security policies.
        Returns (is_allowed: bool, reason: str).
        """
        # 1. Receiver ID Check
        if receiver_id not in self.allowed_receivers:
            return False, f"AccessDenied: Receiver '{receiver_id}' is not authorized in policy."

        # 2. Smart Contract Method Check
        if method_name not in self.allowed_methods:
            return False, f"AccessDenied: Method '{method_name}' is not authorized."

        # 3. Per-Transaction Spending Cap Check
        if amount_usd > self.max_spend_per_tx_usd:
            return False, f"BudgetExceeded: ${amount_usd:.2f} exceeds max per-transaction cap (${self.max_spend_per_tx_usd:.2f})."

        # 4. Daily Cumulative Budget Check
        if (self.spent_today_usd + amount_usd) > self.daily_budget_usd:
            return False, f"BudgetExceeded: Proposed spend would exceed daily budget (${self.daily_budget_usd:.2f})."

        # 5. Remaining NEAR Allowance on Function Call Key Check
        if amount_near > self.allowance_near:
            return False, f"AllowanceExhausted: Requested {amount_near:.3f} NEAR, but remaining allowance is {self.allowance_near:.3f} NEAR."

        return True, "Transaction approved by policy."

    def execute_and_record(
        self,
        task_id: str,
        amount_usd: float,
        amount_near: float,
        receiver_id: str,
        method_name: str,
        mock_tx_hash: Optional[str] = None
    ) -> Receipt:
        """
        Records the expenditure, decrements allowance and budget, and generates a cryptographic receipt.
        """
        allowed, reason = self.evaluate_transaction(amount_usd, amount_near, receiver_id, method_name)
        if not allowed:
            raise PolicyViolation(reason)

        # Update spend tracking
        self.spent_today_usd += amount_usd
        self.allowance_near -= amount_near
        
        tx_hash = mock_tx_hash or f"0x{uuid.uuid4().hex}"
        receipt = Receipt(
            task_id=task_id,
            target_service=receiver_id,
            amount_usd=amount_usd,
            amount_near=amount_near,
            tx_hash=tx_hash
        )
        self.receipts.append(receipt)
        return receipt
