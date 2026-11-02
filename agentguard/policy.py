"""
Motore di Policy e Sicurezza per AgentGuard.
Modella i vincoli delle Function Call Keys di NEAR, impedendo spese non autorizzate.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
import uuid

class Receipt(BaseModel):
    """Ricevuta crittografica e contabile di una spesa effettuata dall'agente."""
    receipt_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    task_id: str
    target_service: str
    amount_usd: float
    amount_near: float
    tx_hash: str
    status: str = "SETTLED"

class PolicyViolation(Exception):
    """Sollevata quando l'agente tenta di violare le regole di spesa."""
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
        
        # Whitelist dei contratti e metodi autorizzati (come nelle Function Call Keys di NEAR)
        self.allowed_receivers = allowed_receivers or ["intents.near", "v1.agent-market.near", "defuse.near"]
        self.allowed_methods = allowed_methods or ["execute_intent", "request_task", "settle_payment"]
        
        # Registro storico delle ricevute
        self.receipts: List[Receipt] = []

    def evaluate_transaction(
        self,
        amount_usd: float,
        amount_near: float,
        receiver_id: str,
        method_name: str
    ) -> Tuple[bool, str]:
        """
        Valuta se una transazione proposta rispetta tutte le policy di sicurezza.
        Ritorna (consentito: bool, motivo: str).
        """
        # 1. Controllo destinatario (Receiver ID)
        if receiver_id not in self.allowed_receivers:
            return False, f"AccessDenied: Receiver '{receiver_id}' non è autorizzato nella policy."

        # 2. Controllo metodo dello smart contract
        if method_name not in self.allowed_methods:
            return False, f"AccessDenied: Metodo '{method_name}' non è autorizzato."

        # 3. Controllo limite per singola transazione
        if amount_usd > self.max_spend_per_tx_usd:
            return False, f"BudgetExceeded: ${amount_usd:.2f} supera il tetto massimo per tx (${self.max_spend_per_tx_usd:.2f})."

        # 4. Controllo budget giornaliero
        if (self.spent_today_usd + amount_usd) > self.daily_budget_usd:
            return False, f"BudgetExceeded: Spesa proposta supererebbe il budget giornaliero (${self.daily_budget_usd:.2f})."

        # 5. Controllo allowance rimanente sulla chiave NEAR
        if amount_near > self.allowance_near:
            return False, f"AllowanceExhausted: Richiesti {amount_near:.3f} NEAR, ma l'allowance residua è {self.allowance_near:.3f} NEAR."

        return True, "Transazione approvata dalla policy."

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
        Registra la spesa e genera lo scontrino contabile, aggiornando budget e allowance.
        """
        allowed, reason = self.evaluate_transaction(amount_usd, amount_near, receiver_id, method_name)
        if not allowed:
            raise PolicyViolation(reason)

        # Aggiorna i bilanci
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
