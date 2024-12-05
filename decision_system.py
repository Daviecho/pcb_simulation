class Decision_System:
    def __init__(self, actions, pcb):
        self.actions = actions  # Lista delle azioni disponibili (test e strategie)
        self.pcb = pcb
        self.observed_state = self.get_observed_state()
        self.executed_tests = set()

    def get_observed_state(self):
        """
        Restituisce lo stato osservato attuale della PCB.
        """
        observed_state = {}
        for component in self.pcb.components:
            observed_state[component.idComponent] = component.defect_probabilities
        return observed_state

    def select_next_action(self):
        """
        Seleziona l'azione migliore tra quelle disponibili.
        """
        best_action = None
        best_value = float("-inf")

        for action in self.actions:
            # Salta i test già eseguiti
            if action.action_type == "test" and action.target.name in self.executed_tests:
                continue

            value = self.calculate_decision_value(action)
            if value > best_value:
                best_value = value
                best_action = action

        if best_action and best_action.action_type == "test":
            self.executed_tests.add(best_action.target.name)

        return best_action

    def calculate_decision_value(self, action):
        """
        Calcola il valore decisionale di una data azione.
        """
        if action.action_type == "test":
            return -action.target.cost  # Valore semplice basato sul costo del test
        elif action.action_type == "strategy":
            return action.target.income - action.target.cost  # Profitto netto della strategia
        return float("-inf")

    def update_observed_state(self, new_state):
        """
        Aggiorna lo stato osservato con un nuovo stato.
        """
        self.observed_state = new_state
