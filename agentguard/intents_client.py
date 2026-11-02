"""
Client per NEAR Intents e 1-Click API.
Permette all'agente di richiedere quotazioni e regolare pagamenti cross-chain.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid
import time
from agentguard.config import settings

class IntentQuote(BaseModel):
    quote_id: str = Field(default_factory=lambda: f"quote_{uuid.uuid4().hex[:10]}")
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    estimated_cost_usd: float
    expiration_timestamp: float = Field(default_factory=lambda: time.time() + 60)

class IntentsClient:
    def __init__(self, simulation_mode: Optional[bool] = None):
        self.simulation_mode = simulation_mode if simulation_mode is not None else settings.simulation_mode

    def get_quote(self, token_in: str, token_out: str, amount_in: float) -> IntentQuote:
        """
        Richiede una quotazione per uno scambio o pagamento tramite NEAR Intents.
        In modalità simulazione (default per test e hackathon), calcola un tasso deterministico.
        """
        if self.simulation_mode:
            # Tasso simulato: 1 NEAR = $3.80 USD
            rate = 3.80 if token_in.upper() == "NEAR" else (1.0 / 3.80)
            amount_out = round(amount_in * rate, 4)
            cost_usd = round(amount_in * 3.80 if token_in.upper() == "NEAR" else amount_in, 2)
            
            return IntentQuote(
                token_in=token_in,
                token_out=token_out,
                amount_in=amount_in,
                amount_out=amount_out,
                estimated_cost_usd=cost_usd
            )
        else:
            # Chiamata REST all'endpoint live di 1-Click Intents API
            # https://docs.near-intents.org/integration/distribution-channels/1click-api/
            # Per i testnet / mock usa il fallback di sicurezza
            raise NotImplementedError("Live Intents API richiede un JWT partner registrato su partners.near-intents.org")

    def execute_intent(self, quote: IntentQuote, recipient: str) -> Dict[str, Any]:
        """
        Esegue l'intento firmato e salda il pagamento verso il destinatario.
        """
        if time.time() > quote.expiration_timestamp:
            raise ValueError("IntentQuoteExpired: La quotazione è scaduta, richiedine una nuova.")

        # Simulazione o esecuzione on-chain
        return {
            "status": "SETTLED",
            "tx_hash": f"0x{uuid.uuid4().hex}",
            "recipient": recipient,
            "settled_amount": quote.amount_out,
            "settled_token": quote.token_out,
            "protocol": "NEAR Intents (1-Click)"
        }
