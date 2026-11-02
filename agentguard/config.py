"""
Configuration Module for AgentGuard.
Loads and validates settings for NEAR, NEAR AI Cloud, and budget policy limits.
"""

import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Settings(BaseModel):
    # NEAR Network Parameters
    near_network: str = Field(default_factory=lambda: os.getenv("NEAR_NETWORK", "testnet"))
    near_rpc_url: str = Field(default_factory=lambda: os.getenv("NEAR_RPC_URL", "https://rpc.testnet.near.org"))
    near_account_id: str = Field(default_factory=lambda: os.getenv("NEAR_ACCOUNT_ID", "agentguard.testnet"))
    near_private_key: str = Field(default_factory=lambda: os.getenv("NEAR_PRIVATE_KEY", "ed25519:mock_key_for_testing"))

    # NEAR AI Cloud Parameters (https://cloud.near.ai)
    near_ai_base_url: str = Field(default_factory=lambda: os.getenv("NEAR_AI_BASE_URL", "https://api.near.ai/v1"))
    near_ai_api_key: str = Field(default_factory=lambda: os.getenv("NEAR_AI_API_KEY", "mock-key"))
    near_ai_model: str = Field(default_factory=lambda: os.getenv("NEAR_AI_MODEL", "meta-llama/Llama-3.1-70B-Instruct"))

    # Spending & Security Policy Limits
    max_spend_per_tx_usd: float = Field(default_factory=lambda: float(os.getenv("MAX_SPEND_PER_TX_USD", "2.00")))
    daily_budget_usd: float = Field(default_factory=lambda: float(os.getenv("DAILY_BUDGET_USD", "5.00")))
    max_allowance_near: float = Field(default_factory=lambda: float(os.getenv("MAX_ALLOWANCE_NEAR", "2.00")))

    # Execution Mode (True = offline/mock for fast automated testing and screening)
    simulation_mode: bool = Field(
        default_factory=lambda: os.getenv("SIMULATION_MODE", "true").lower() in ("true", "1", "yes")
    )

settings = Settings()
