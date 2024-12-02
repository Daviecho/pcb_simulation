class Strategy:
    def __init__(self, idStrategy, name, cost, income):
        self.idStrategy = idStrategy
        self.name = name  
        self.cost = cost
        self.income = income


    def calculate_profit(self):
        """
        Calculates the profit for this strategy.
        
        Returns:
        - Profit as income minus cost.
        """
        return self.income - self.cost
