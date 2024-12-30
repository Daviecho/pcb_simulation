# decision_system.py
import random
from agent import DQNAgent
import torch

class Decision_System:
    def __init__(self, agent, actions, gnn_model):
        self.agent = agent
        self.actions = actions  # List of Action instances
        self.gnn_model = gnn_model  # GNN model for state representation

    # def select_next_action(self, pcb, available_actions):
    #     """
    #     Selects the next action using the RL agent.
    #     """
    #     action = self.agent.select_action(pcb, available_actions)
    #     return action
    
    def select_next_action(self, pcb, available_actions):
        """
        Selects the next action randomly from the available actions.
        """
        if not available_actions:
            return None  # No actions available

        action_idx = random.choice(available_actions)
        return action_idx
