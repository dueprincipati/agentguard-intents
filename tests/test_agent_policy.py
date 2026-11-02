"""
Suite di Test Automatici per AgentGuard (Policy, NEAR Intents e Agent Loop).
Testata con pytest per la verifica di riproducibilità da parte dei giudici dell'Hackathon.
"""

import pytest
from agentguard.policy import PolicyEngine, PolicyViolation
from agentguard.intents_client import IntentsClient
from agentguard.agent import AgentGuard

def test_policy_allows_valid_transaction():
    """Verifica che una transazione lecita entro i limiti venga approvata."""
    pe = PolicyEngine(max_spend_per_tx_usd=2.0, max_allowance_near=2.0)
    allowed, reason = pe.evaluate_transaction(
        amount_usd=1.20,
        amount_near=0.31,
        receiver_id="intents.near",
        method_name="execute_intent"
    )
    assert allowed is True
    assert "approvata" in reason

def test_policy_rejects_unauthorized_receiver():
    """Verifica che un contratto sconosciuto o malevolo venga respinto (AccessDenied)."""
    pe = PolicyEngine()
    allowed, reason = pe.evaluate_transaction(
        amount_usd=0.50,
        amount_near=0.1,
        receiver_id="hacker_contract.near",
        method_name="execute_intent"
    )
    assert allowed is False
    assert "AccessDenied" in reason

def test_policy_rejects_exceeding_single_tx_budget():
    """Verifica che importi superiori al tetto massimo per singola tx vengano bloccati."""
    pe = PolicyEngine(max_spend_per_tx_usd=2.00)
    allowed, reason = pe.evaluate_transaction(
        amount_usd=3.50,
        amount_near=0.9,
        receiver_id="intents.near",
        method_name="execute_intent"
    )
    assert allowed is False
    assert "BudgetExceeded" in reason

def test_policy_rejects_exceeding_allowance():
    """Verifica che l'agente non possa spendere più NEAR dell'allowance della sua chiave."""
    pe = PolicyEngine(max_allowance_near=1.0)
    allowed, reason = pe.evaluate_transaction(
        amount_usd=1.50,
        amount_near=1.5,  # Richiede più dell'allowance
        receiver_id="intents.near",
        method_name="execute_intent"
    )
    assert allowed is False
    assert "AllowanceExhausted" in reason

def test_intents_quote_generation():
    """Verifica il calcolo corretto della quotazione NEAR Intents."""
    client = IntentsClient(simulation_mode=True)
    quote = client.get_quote(token_in="NEAR", token_out="USDC", amount_in=1.0)
    assert quote.token_out == "USDC"
    assert quote.amount_out > 0
    assert quote.estimated_cost_usd > 0

def test_agent_end_to_end_execution():
    """Verifica il ciclo vitale completo: pianificazione, policy, esecuzione e scontrino."""
    agent = AgentGuard()
    initial_allowance = agent.policy.allowance_near
    
    result = agent.run_task("Acquisto dati oracolo cross-chain", budget_usd=2.0)
    
    assert result["success"] is True
    assert "receipt" in result
    assert result["receipt"]["status"] == "SETTLED"
    assert result["remaining_allowance_near"] < initial_allowance
    assert result["total_spent_today_usd"] > 0
