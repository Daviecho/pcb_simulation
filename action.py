# action.py
import random

class Action:
    def __init__(self, action_type, target, cost, duration):
        self.action_type = action_type  # "test" or "strategy"
        self.target = target  # Measurement or Strategy instance
        self.cost = cost
        self.duration = duration

    def execute(self, pcb, env):
        """
        Executes the action on the PCB within the given environment.
        Returns the result of the action.
        """
        if self.action_type == "test":
            # Execute the measurement
            result = yield env.process(self.target.execute(pcb))
            return result
        elif self.action_type == "strategy":
            # Execute the strategy
            result = self.target.execute(pcb)
            return result
        else:
            raise ValueError("Unknown action type.")
