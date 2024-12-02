from action import Action

class Decision_System:
    def __init__(self, measurements, pcb, strategies):
        self.measurements = measurements
        self.pcb = pcb
        self.strategies = strategies
        self.executed_tests = set()  # Traccia i test già eseguiti

    def process_decision(self):
        """
        Itera sul processo decisionale per determinare la sequenza di test e la strategia finale.
        """
        observed_state = self.get_observed_state()
        test_sequence = []
        max_iterations = 20
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"Iteration {iteration}, Observed state: {observed_state}")

            # Richiedi la prossima azione
            action = Action.decide_next_action(
                observed_state,
                self.measurements,
                self.strategies,
                executed_tests=self.executed_tests
            )

            if action.action_type == "test":
                # Esegui il test e aggiorna lo stato osservato
                result = action.execute(observed_state, self.pcb)
                observed_state = result["observed_state"]
                test_sequence.append(action.target.nameMeasurement)
                self.executed_tests.add(action.target.nameMeasurement)  # Segna il test come eseguito
                print(f"Executed test: {action.target.nameMeasurement}")
            elif action.action_type == "strategy":
                print(f"Strategy chosen: {action.target.name}")
                return {
                    "test_sequence": test_sequence,
                    "strategy": action.target.name,
                    "income": result.get("income", 0)
                }

        print("Max iterations reached. Defaulting to 'NoStrategy'.")
        return {
            "test_sequence": test_sequence,
            "strategy": "NoStrategy",
            "income": 0
        }




    def get_observed_state(self):
        """
        Restituisce lo stato osservato attuale della PCB.
        """
        observed_state = {}
        for component in self.pcb.components:
            observed_state[component.idComponent] = component.defect_probabilities
        return observed_state
