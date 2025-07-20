# agent_registry.py

from agents.intake_agent import IntakeAgent
from agents.cafe_bot import LanscapeCafeBot
from agents.database_agent import CoffeeDatabaseAgent
from agents.aggregator_agent import AggregatorAgent

AGENT_REGISTRY = {
    "intake_agent": IntakeAgent,
    "landscape_cafe_bot": LanscapeCafeBot,
    "coffee_db_agent": CoffeeDatabaseAgent,
    "aggregator_agent": AggregatorAgent,
} 