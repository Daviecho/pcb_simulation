# strategy.py

class Strategy:
    def __init__(self, idStrategy, name, cost, income):
        self.idStrategy = idStrategy
        self.name = name  # "Reuse", "Repair", or "Recycle"
        self.cost = cost
        self.income = income  # Negative income represents a return

    def execute(self, pcb):
        """
        Executes the strategy on the PCB.
        Returns the income (profit) based on the strategy's outcome.
        """
        # For simplicity, assume strategies always succeed
        # You can introduce probabilities for success/failure

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
            # Assume repair is always successful for simplicity
            profit = self.income
        elif self.name == "Recycle":
            # Recycle has a static return
            profit = self.income
        else:
            profit = 0

        return {"income": profit - self.cost}
