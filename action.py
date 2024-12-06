import random

class Action:
    def __init__(self, action_type, target, cost, duration):
        self.action_type = action_type  # "test" or "strategy"
        self.target = target
        self.cost = cost
        self.duration = duration

    def execute(self, real_state):
        if self.action_type == "test":
            # Calling the different measurement method 
            if self.target.name == "X-Ray":
                return self.xray(real_state)
            elif self.target.name == "Visual Inspection":
                return self.visual_inspection(real_state)
            elif self.target.name == "Flying Probe":
                return self.flying_probe(real_state)
        elif self.action_type == "strategy":
            return {"income": self.target.income - self.target.cost}

    def xray(self, real_state):
        observed_state = {}
        for component_id, defects in real_state.items():
            observed_state[component_id] = {}
            for defect_name, probability in defects.items():
                # Simulates the observation 
                if random.random() < self.target.get_accuracy(defect_name):
                    # Updating the probability increasing issue certainty 
                    observed_state[component_id][defect_name] = min(1.0, probability + random.uniform(0.1, 0.3))
                else:
                    # Decreasing the probability if not detected
                    observed_state[component_id][defect_name] = max(0.0, probability - random.uniform(0.1, 0.2))
        return {"observed_state": observed_state, "cost": self.target.cost}

    def visual_inspection(self, real_state):
        observed_state = {}
        for component_id, defects in real_state.items():
            observed_state[component_id] = {}
            for defect_name, probability in defects.items():
                # Simulates the observation 
                if random.random() < self.target.get_accuracy(defect_name):
                    observed_state[component_id][defect_name] = min(1.0, probability + random.uniform(0.05, 0.2))
                else:
                    observed_state[component_id][defect_name] = max(0.0, probability - random.uniform(0.05, 0.1))
        return {"observed_state": observed_state, "cost": self.target.cost}

    def flying_probe(self, real_state):
        observed_state = {}
        for component_id, defects in real_state.items():
            observed_state[component_id] = {}
            for defect_name, probability in defects.items():
                # Simulates the observation 
                if random.random() < self.target.get_accuracy(defect_name):
                    observed_state[component_id][defect_name] = min(1.0, probability + random.uniform(0.15, 0.35))
                else:
                    observed_state[component_id][defect_name] = max(0.0, probability - random.uniform(0.1, 0.15))
        return {"observed_state": observed_state, "cost": self.target.cost}
