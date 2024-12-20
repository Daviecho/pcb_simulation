class Component:
    def __init__(self, idComponent, defect_probabilities, componentTypeName="", state="noDefect"):
        self.idComponent = idComponent
        self.defect_probabilities = defect_probabilities  # Dizionario delle probabilità di difetti
        self.componentTypeName = componentTypeName  # Tipo del componente
        self.state = state  # Stato del componente (es. defect, noDefect)


    def update_state(self, observed_state):
        """
        Updates the observed state of the component based on a test result.
        """
        self.observed_state = observed_state

class PCB:
    def __init__(self, idPCB, PCBTypeName, components):
        self.idPCB = idPCB
        self.PCBTypeName = PCBTypeName
        self.components = components  # Lista di componenti
        self.income = 0

    def add_component(self, component):
        self.components.append(component)

