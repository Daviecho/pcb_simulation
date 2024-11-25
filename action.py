class Action:
    def __init__(self, pcb, measurements, strategies):
        self.pcb = pcb  # PCB object being analyzed
        self.measurements = measurements  # List of Measurement objects
        self.strategies = strategies  # List of strategy objects

    def get_measurements(self):
        """Returns the list of measurements available for the PCB."""
        return self.measurements

    def get_strategies(self):
        """Returns the list of strategies available for the PCB."""
        return self.strategies
