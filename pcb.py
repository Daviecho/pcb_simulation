class Component:
    def __init__(self, idComponent, state, componentTypeName):
        self.idComponent = idComponent
        self.state = state  # "defect" or "noDefect"
        self.componentTypeName = componentTypeName
        self.defect_probabilities = {}

    def set_defect_probability(self, defect_name, probability):
        """Sets the probability of a specific defect for this component."""
        if 0 <= probability <= 1:
            self.defect_probabilities[defect_name] = probability
        else:
            raise ValueError("Probability must be between 0 and 1.")

class PCB:
    def __init__(self, idPCB, PCBTypeName):
        self.idPCB = idPCB
        self.PCBTypeName = PCBTypeName
        self.components = []  # List of Component objects

    def add_component(self, component):
        """Adds a component to the PCB."""
        self.components.append(component)

