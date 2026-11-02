"""
Entrypoint CLI per AgentGuard.
Interfaccia a riga di comando per avviare l'agente e verificare le policy di sicurezza.
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
        default="Analizza liquidita DEX cross-chain e acquista report di mercato",
        help="Descrizione del task affidato all'agente"
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=2.00,
        help="Budget massimo autorizzato in USD (default: $2.00)"
    )
    parser.add_argument(
        "--simulate-attack",
        action="store_true",
        help="Simula un tentativo di spesa fuori policy o non autorizzata"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Mostra lo stato attuale del wallet e dell'allowance residua"
    )

    args = parser.parse_args()
    agent = AgentGuard()

    print("=" * 60)
    print("🛡️  AGENTGUARD: Autonomous AI Agent on NEAR Protocol")
    print("=" * 60)

    if args.status:
        print(f"Network: {agent.policy.allowed_receivers}")
        print(f"Allowance NEAR residua: {agent.policy.allowance_near:.3f} NEAR")
        print(f"Speso oggi: ${agent.policy.spent_today_usd:.2f} / ${agent.policy.daily_budget_usd:.2f} USD")
        return

    if args.simulate_attack:
        print("\n⚠️  [TEST DI SICUREZZA] Simulazione di transazione anomala / attacco:")
        print("Tentativo di inviare $15.00 a un contratto non autorizzato ('malicious-dapp.near')...")
        attack_res = agent.policy.evaluate_transaction(
            amount_usd=15.00,
            amount_near=4.0,
            receiver_id="malicious-dapp.near",
            method_name="steal_funds"
        )
        print(f"Esito: {'Consentito' if attack_res[0] else 'BLOCCATO DALLA POLICY'}")
        print(f"Motivo del blocco: {attack_res[1]}")
        print("=" * 60)
        return

    print(f"\n[1] Ricevuto Task: \"{args.task}\"")
    print(f"[2] Budget stanziato: ${args.budget:.2f} USD")
    print("\n[3] Esecuzione in corso (NEAR AI -> Policy Guard -> NEAR Intents)...")
    
    result = agent.run_task(task_description=args.task, budget_usd=args.budget)
    
    if result["success"]:
        print("\n✅ TASK COMPLETATO CON SUCCESSO!")
        print(f"Piano: {result['plan_summary']}")
        print(f"Scontrino Contabile: {result['receipt']['receipt_id']}")
        print(f"Importo regolato: ${result['receipt']['amount_usd']:.2f} ({result['receipt']['amount_near']:.3f} NEAR)")
        print(f"Tx Hash: {result['receipt']['tx_hash']}")
        print(f"Allowance NEAR rimanente: {result['remaining_allowance_near']} NEAR")
        print(f"Totale speso oggi: ${result['total_spent_today_usd']} USD")
    else:
        print("\n❌ OPERAZIONE NEGATA DALLA POLICY:")
        print(f"Motivo: {result['reason']}")

    print("=" * 60)

if __name__ == "__main__":
    main()
