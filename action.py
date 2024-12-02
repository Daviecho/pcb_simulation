class Action:
    def __init__(self, action_type, target, duration=0, cost=0):
        self.action_type = action_type
        self.target = target
        self.duration = duration
        self.cost = cost


    @staticmethod
    def decide_next_action(observed_state, measurements, strategies, executed_tests=None):
        """
        Determina l'azione successiva basandosi sull'observed_state e i test già eseguiti.
        """
        executed_tests = executed_tests or set()

        # Filtra i test disponibili escludendo quelli già eseguiti
        available_measurements = [
            m for m in measurements if m.nameMeasurement not in executed_tests
        ]

        # Se ci sono test disponibili, seleziona il primo come esempio
        if available_measurements:
            target = available_measurements[0]
            return Action("test", target, duration=target.duration, cost=target.cost)

        # Se non ci sono test disponibili, seleziona la strategia "Recycle"
        recycle_strategy = next((s for s in strategies if s.name == "Recycle"), None)
        if recycle_strategy:
            return Action("strategy", recycle_strategy, duration=0, cost=0)

        # Caso eccezionale: nessuna azione valida trovata
        raise ValueError("No valid tests or strategies available, and 'Recycle' not defined.")


    @staticmethod
    def state_to_key(observed_state):
        """
        Converte lo stato osservato in una chiave univoca.
        """
        key_parts = []
        for component_id, defects in observed_state.items():
            for defect_name, value in defects.items():
                key_parts.append(f"{component_id}:{defect_name}:{value}")
        return ",".join(sorted(key_parts))

    def execute(self, observed_state, pcb):
        """
        Simula l'esecuzione dell'azione.
        """
        if self.action_type == "test":
            # Simula un risultato per il test
            new_observed_state = observed_state.copy()
            for component_id, defects in new_observed_state.items():
                for defect_name in defects.keys():
                    # Aggiorna lo stato con probabilità semplificate
                    new_observed_state[component_id][defect_name] = 1 if defects[defect_name] > 0 else 0
            return {"observed_state": new_observed_state}
        elif self.action_type == "strategy":
            # Restituisci il risultato della strategia
            return {"observed_state": observed_state, "income": self.target.income - self.target.cost}
