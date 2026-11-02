"""
CLI Entrypoint for AgentGuard.
Command-line interface to execute the autonomous agent and verify security policies.
"""

import argparse
import json
from agentguard.agent import AgentGuard

def main():
    parser = argparse.ArgumentParser(
        description="AgentGuard: Autonomous AI Agent with NEAR Function Call Key Security & Intents"
    )
    parser.add_argument(
        "--task",
        type=str,
        default="Analyze cross-chain DEX liquidity and purchase market report",
        help="Description of the task assigned to the agent"
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=2.00,
        help="Maximum authorized budget in USD (default: $2.00)"
    )
    parser.add_argument(
        "--simulate-attack",
        action="store_true",
        help="Simulate an unauthorized or out-of-policy transaction attempt"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display current wallet status and remaining allowance"
    )

    args = parser.parse_args()
    agent = AgentGuard()

    print("=" * 60)
    print("🛡️  AGENTGUARD: Autonomous AI Agent on NEAR Protocol")
    print("=" * 60)

    if args.status:
        print(f"Allowed receivers: {agent.policy.allowed_receivers}")
        print(f"Remaining NEAR allowance: {agent.policy.allowance_near:.3f} NEAR")
        print(f"Spent today: ${agent.policy.spent_today_usd:.2f} / ${agent.policy.daily_budget_usd:.2f} USD")
        return

    if args.simulate_attack:
        print("\n⚠️  [SECURITY TEST] Simulating anomalous/malicious transaction attempt:")
        print("Attempting to send $15.00 to unauthorized contract ('malicious-dapp.near')...")
        attack_res = agent.policy.evaluate_transaction(
            amount_usd=15.00,
            amount_near=4.0,
            receiver_id="malicious-dapp.near",
            method_name="steal_funds"
        )
        print(f"Result: {'Allowed' if attack_res[0] else 'BLOCKED BY POLICY'}")
        print(f"Block Reason: {attack_res[1]}")
        print("=" * 60)
        return

    print(f"\n[1] Received Task: \"{args.task}\"")
    print(f"[2] Allocated Budget: ${args.budget:.2f} USD")
    print("\n[3] Execution in progress (NEAR AI -> Policy Guard -> NEAR Intents)...")
    
    result = agent.run_task(task_description=args.task, budget_usd=args.budget)
    
    if result["success"]:
        print("\n✅ TASK COMPLETED SUCCESSFULLY!")
        print(f"Plan: {result['plan_summary']}")
        print(f"Accounting Receipt: {result['receipt']['receipt_id']}")
        print(f"Settled Amount: ${result['receipt']['amount_usd']:.2f} ({result['receipt']['amount_near']:.3f} NEAR)")
        print(f"Tx Hash: {result['receipt']['tx_hash']}")
        print(f"Remaining NEAR Allowance: {result['remaining_allowance_near']} NEAR")
        print(f"Total Spent Today: ${result['total_spent_today_usd']} USD")
    else:
        print("\n❌ OPERATION DENIED BY POLICY:")
        print(f"Reason: {result['reason']}")

    print("=" * 60)

if __name__ == "__main__":
    main()
