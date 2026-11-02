"""
Automated Test Suite for AgentGuard (Policy, NEAR Intents, and Agent Loop).
Tested with pytest for reproducibility check by Hackathon judges.
"""

import pytest
from agentguard.policy import PolicyEngine, PolicyViolation
from agentguard.intents_client import IntentsClient
from agentguard.agent import AgentGuard

def test_policy_allows_valid_transaction():
    """Verify that a legitimate transaction within limits is approved."""
    pe = PolicyEngine(max_spend_per_tx_usd=2.0, max_allowance_near=2.0)
    allowed, reason = pe.evaluate_transaction(
        amount_usd=1.20,
        amount_near=0.31,
        receiver_id="intents.near",
        method_name="execute_intent"
    )
    assert allowed is True
    assert "approved" in reason.lower()

def test_policy_rejects_unauthorized_receiver():
    """Verify that an unauthorized or malicious contract is rejected (AccessDenied)."""
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
    """Verify that transactions exceeding the per-tx spending cap are rejected."""
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
    """Verify that the agent cannot spend more NEAR than its Function Call Key allowance."""
    pe = PolicyEngine(max_allowance_near=1.0)
    allowed, reason = pe.evaluate_transaction(
        amount_usd=1.50,
        amount_near=1.5,  # Exceeds allowance
        receiver_id="intents.near",
        method_name="execute_intent"
    )
    assert allowed is False
    assert "AllowanceExhausted" in reason

def test_intents_quote_generation():
    """Verify accurate NEAR Intents swap quote calculation."""
    client = IntentsClient(simulation_mode=True)
    quote = client.get_quote(token_in="NEAR", token_out="USDC", amount_in=1.0)
    assert quote.token_out == "USDC"
    assert quote.amount_out > 0
    assert quote.estimated_cost_usd > 0

def test_agent_end_to_end_execution():
    """Verify complete lifecycle: planning, policy check, intent settlement, and receipt generation."""
    agent = AgentGuard()
    initial_allowance = agent.policy.allowance_near
    
    result = agent.run_task("Cross-chain oracle data purchase", budget_usd=2.0)
    
    assert result["success"] is True
    assert "receipt" in result
    assert result["receipt"]["status"] == "SETTLED"
    assert result["remaining_allowance_near"] < initial_allowance
    assert result["total_spent_today_usd"] > 0
