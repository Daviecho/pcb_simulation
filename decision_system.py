from action import Action

class Decision_System:
    def __init__(self, measurements, strategies, pcb):
        self.measurements = measurements
        self.strategies = strategies
        self.pcb = pcb
        self.observed_state = self.get_observed_state()
        self.executed_tests = set()

    def get_observed_state(self):
        observed_state = {}
        for component in self.pcb.components:
            observed_state[component.idComponent] = component.defect_probabilities
        return observed_state

    def calculate_decision_value(self, action):
        if action.action_type == "test":
            total_value = 0
            for component_id, defects in self.observed_state.items():
                for defect_name, probability in defects.items():
                    likelihood = probability * action.target.get_accuracy(defect_name)
                    total_value += likelihood * (action.target.cost * -1)  # Simplified profit
            return total_value - action.cost
        elif action.action_type == "strategy":
            return action.target.income - action.target.cost

    def select_next_action(self):
        all_actions = [
            Action("test", m, m.cost, m.duration) for m in self.measurements if m.name not in self.executed_tests
        ] + [
            Action("strategy", s, s.cost, 0) for s in self.strategies
        ]

        best_action = None
        best_value = float("-inf")
        for action in all_actions:
            value = self.calculate_decision_value(action)
            if value > best_value:
                best_value = value
                best_action = action

        if best_action and best_action.action_type == "test":
            self.executed_tests.add(best_action.target.name)

        return best_action

    def update_observed_state(self, new_state):
        self.observed_state = new_state
