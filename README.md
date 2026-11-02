# AgentGuard-Intents

> Autonomous task contractor agent with policy-enforced wallets via NEAR Function Call Keys and cross-chain execution through NEAR Intents.

Built for **NEAR HACKATHON 2026**  
**Target Tracks:** `agents` (Agent Economy), `security` (AI Security & Defense), `business` (Autonomous Business).

---

## 1. Problem & Solution

* **The Problem:** AI agents operating autonomously need to pay for sub-tasks, compute, and external data. However, granting an AI agent custody of a full-access crypto wallet exposes user treasuries to drainage, prompt injection exploits, or out-of-control spending loops.
* **The NEAR Solution:** **AgentGuard** leverages NEAR Protocol's native **Function Call Access Keys** and **NEAR Intents**:
  1. The agent is granted a restricted key bound to specific contract receivers (`intents.near`, `defuse.near`) and a hardcoded allowance.
  2. A local deterministic **Policy Engine** evaluates every transaction against per-tx caps, daily budgets, and contract whitelists before signing.
  3. Payments are settled cross-chain via **NEAR Intents (1-Click API)**, producing an immutable cryptographic receipt for every completed task.

---

## 2. NEAR Technologies Used

* **Function Call Access Keys:** Restricts signing rights strictly to whitelisted smart contracts and caps the maximum spendable NEAR allowance at the protocol level.
* **NEAR Intents (1-Click API):** Enables seamless cross-chain payments and token swaps (NEAR to USDC) without managing multi-chain gas or bridge risks.
* **NEAR AI Cloud (`https://api.near.ai/v1`):** Powers the agent's task decomposition and reasoning loop using open-weights models (Llama 3.1) in private compute environments.

---

## 3. Quickstart & Verification ("Do X, See Y")

Follow these steps to reproduce and verify the agent's execution locally.

### Step 1: Environment Setup
Clone the repository, create a virtual environment, and install dependencies:
```bash
git clone https://github.com/dueprincipati/agentguard-intents.git
cd agentguard-intents
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
**Expected Output:** All dependencies installed cleanly with zero conflicts.

---

### Step 2: Run Automated Tests
Execute the formal test suite covering policy enforcement, allowance caps, and intent execution:
```bash
pytest -v
```
**Expected Output:**
```text
tests/test_agent_policy.py::test_policy_allows_valid_transaction PASSED
tests/test_agent_policy.py::test_policy_rejects_unauthorized_receiver PASSED
tests/test_agent_policy.py::test_policy_rejects_exceeding_single_tx_budget PASSED
tests/test_agent_policy.py::test_policy_rejects_exceeding_allowance PASSED
tests/test_agent_policy.py::test_intents_quote_generation PASSED
tests/test_agent_policy.py::test_agent_end_to_end_execution PASSED
====== 6 passed in 0.08s ======
```

---

### Step 3: Run the Autonomous Agent Loop
Run the agent with a sample task and a $2.00 USD budget:
```bash
python3 main.py --task "Analizza liquidita DEX cross-chain e acquista report di mercato" --budget 2.00
```
**Expected Output:**
```text
[1] Ricevuto Task: "Analizza liquidita DEX cross-chain e acquista report di mercato"
[2] Budget stanziato: $2.00 USD
[3] Esecuzione in corso (NEAR AI -> Policy Guard -> NEAR Intents)...

✅ TASK COMPLETATO CON SUCCESSO!
Piano: Esecuzione controllata del task: 'Analizza liquidita DEX cross-chain e acquista report di mercato'
Scontrino Contabile: rec_xxxxxxxxxxxx
Importo regolato: $1.50 (0.395 NEAR)
Tx Hash: 0x...
Allowance NEAR rimanente: 1.605 NEAR
Totale speso oggi: $1.5 USD
```

---

### Step 4: Verify Policy Defense (Simulated Attack / Exploitation Attempt)
Test the agent's policy firewall by simulating an unauthorized transfer to an unapproved contract:
```bash
python3 main.py --simulate-attack
```
**Expected Output:**
```text
⚠️  [TEST DI SICUREZZA] Simulazione di transazione anomala / attacco:
Tentativo di inviare $15.00 a un contratto non autorizzato ('malicious-dapp.near')...
Esito: BLOCCATO DALLA POLICY
Motivo del blocco: AccessDenied: Receiver 'malicious-dapp.near' non è autorizzato nella policy.
```

---

## 4. Project Structure

```text
agentguard-intents/
├── agentguard/
│   ├── __init__.py
│   ├── config.py           # Configuration & environment validation (Pydantic)
│   ├── policy.py           # Policy Engine & Function Call Key guard
│   ├── near_ai_client.py   # NEAR AI Cloud client (https://api.near.ai/v1)
│   ├── intents_client.py   # NEAR Intents & 1-Click execution client
│   └── agent.py            # Master ReAct Agent coordinator loop
├── tests/
│   ├── __init__.py
│   └── test_agent_policy.py# Automated pytest test suite (6 test cases)
├── main.py                 # CLI entrypoint for testing and verification
├── requirements.txt        # Pinned dependencies
├── LICENSE                 # MIT License
└── README.md               # Documentation and reproducibility guide
```

---

## 5. License
MIT License - Copyright (c) 2026 Massimo Testa.
