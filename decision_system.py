class Decision_System:
    def __init__(self, actions, pcb):
        self.actions = actions
        self.pcb = pcb
        self.executed_tests = []

    # Select the next action with the highest decision value
    def select_next_action(self):
        best_action = None
        max_value = float("-inf")

        for action in self.actions:
            if action.action_type == "test" and action.target.name in self.executed_tests:
                continue  # Skip tests that have already been executed
            decision_value = self.calculate_decision_value(action)
            if decision_value > max_value:
                max_value = decision_value
                best_action = action

        if best_action and best_action.action_type == "test":
            self.executed_tests.append(best_action.target.name)
        return best_action

    # Decision value logic
    def calculate_decision_value(self, action):
        total_value = 0
        if action.action_type == "test":
            for component in self.pcb.components:
                # Use the state of the component to calculate the decision value
                defect_name = component.state
                if defect_name and defect_name != "no_defect":  # Skip if no defect
                    total_value += action.target.get_accuracy(defect_name) * (1 - action.target.cost)
        elif action.action_type == "strategy":
            total_value = action.target.income - action.target.cost
        return total_value
