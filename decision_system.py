class Decision_System:
    def __init__(self, measurements, pcb, strategies):
        self.measurements = measurements  # List of available Measurement objects
        self.pcb = pcb  # The PCB being analyzed
        self.strategies = strategies  # List of strategy objects

    def calculate_decision_value(self, test, strategy):
        """
        Calculates the decision value V(T_i, S_k) for a given test and strategy.
        """
        total_value = 0

        # Iterate over each component and its defect probabilities
        for component in self.pcb.components:
            for defect_name, prior_probability in component.defect_probabilities.items():
                # Get test accuracy for the defect
                P_Ti_Dj = test.get_accuracy(defect_name)

                # Calculate likelihood and decision value contribution
                likelihood = P_Ti_Dj * prior_probability
                profit_contribution = likelihood * strategy.calculate_profit()
                total_value += profit_contribution

        # Subtract the test cost
        total_value -= test.cost
        return total_value

    def select_best_strategy(self):
        """
        Selects the best sequence of tests and the optimal strategy for the PCB.
        """
        best_sequence = []
        best_strategy = None
        max_value = float("-inf")

        # Try each strategy
        for strategy in self.strategies:
            remaining_measurements = self.measurements[:]
            sequence = []
            total_value = 0

            # Iteratively select tests
            while remaining_measurements:
                best_test = None
                best_test_value = float("-inf")

                for test in remaining_measurements:
                    test_value = self.calculate_decision_value(test, strategy)
                    if test_value > best_test_value:
                        best_test_value = test_value
                        best_test = test

                if best_test:
                    sequence.append(best_test)
                    total_value += best_test_value
                    remaining_measurements.remove(best_test)

            # Compare strategy value
            if total_value > max_value:
                max_value = total_value
                best_sequence = sequence
                best_strategy = strategy

        self.update_defect_probabilities(best_sequence)
        return best_sequence, best_strategy

    def update_defect_probabilities(self, sequence):
        """
        Updates defect probabilities for each component based on the executed test sequence.
        """
        for test in sequence:
            for component in self.pcb.components:
                updated_probabilities = {}
                total_probability = 0

                # Update probabilities for each defect
                for defect_name, prior_probability in component.defect_probabilities.items():
                    P_Ti_Dj = test.get_accuracy(defect_name)
                    likelihood = P_Ti_Dj * prior_probability
                    updated_probabilities[defect_name] = likelihood
                    total_probability += likelihood

                # Normalize probabilities
                for defect_name in updated_probabilities:
                    if total_probability > 0:
                        component.defect_probabilities[defect_name] = updated_probabilities[defect_name] / total_probability
                    else:
                        component.defect_probabilities[defect_name] = 0
