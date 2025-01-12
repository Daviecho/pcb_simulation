# strategy.py

class Strategy:
    def __init__(self, idStrategy, name, cost, income, repair_cost=0):
        self.idStrategy = idStrategy
        self.name = name  # "Reuse", "Repair", or "Recycle"
        self.cost = cost
        self.income = income  # Negative income represents a return
        self.repair_cost = repair_cost  # Applicable only for "Repair"

    def execute(self, pcb):
        """
        Executes the strategy on the PCB.
        Returns the income (profit) based on the strategy's outcome.
        """
        # For simplicity, assume strategies always succeed
        # You can introduce probabilities for success/failure
        profit = 0
        # Example logic:
        if self.name == "Reuse":
            # Reuse components if they are not broken
            # Assuming 'noDefect' means reusable
            reusable = all(component.state == "noDefect" for component in pcb.components)
            if reusable:
                profit = self.income  # Positive return
            else:
                profit = 0  # No return if components are defective
        elif self.name == "Repair":
            total_repairs = 0
            for component in pcb.components:
                # Check observed_state for defects and repair them
                for defect, observed_prob in component.observed_state.items():
                    if defect != "noDefect" and observed_prob > 0.5:  # Threshold for detected defect; currently not working because measurements is setting prob always to 1!
                        if component.state == defect:  # Successfull Repair only if the observed defect matches the real defect
                            component.finalstate = "noDefect"  # Repair the defect
                        total_repairs += 1

            total_cost = self.repair_cost * total_repairs
            profit -= total_cost  # Subtract total repair costs

            # Verify if all defects were repaired
            if all(component.finalstate == "noDefect" for component in pcb.components):
                profit += self.income  # Add income if all defects are accounted for

        elif self.name == "Recycle":
            # Recycle has a static return
            profit = self.income
        else:
            profit = 0

        return {"income": profit - self.cost}
