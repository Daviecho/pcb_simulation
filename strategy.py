class strategy:
    def __init__(self, name, cost, income):
        self.name = name  # Name of the strategy (e.g., "reuse")
        self.cost = cost  # Cost of applying the strategy
        self.income = income  # Income generated by the strategy

    def calculate_profit(self):
        """Calculates the net profit for the strategy."""
        return self.income - self.cost