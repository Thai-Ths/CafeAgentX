from abc import ABC, abstractmethod
from typing import Dict

class BaseAgent(ABC):
    """
    Abstract base class for all agents in SupportFlowX.
    Every agent must implement the process(state: dict) -> dict method.
    """
    @abstractmethod
    def process(self, state: Dict) -> Dict:
        """
        Process the input state and return a result dict.
        Args:
            state (dict): The input state for the agent.
        Returns:
            dict: The output/result from the agent.
        """
        pass



