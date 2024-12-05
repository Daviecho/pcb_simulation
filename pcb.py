class PCB:
    def __init__(self, idPCB, PCBTypeName, components, real_state = None):
        self.idPCB = idPCB
        self.PCBTypeName = PCBTypeName
        self.components = components
        self.real_state = real_state if real_state else self.initialize_real_state()
        self.current_profit = 0

    def initialize_real_state(self):
        """
        Inizializza il real_state basato sui componenti della PCB.
        """
        real_state = {}
        for component in self.components:
            real_state[component.idComponent] = component.defect_probabilities
        return real_state

    def update_real_state(self, observed_state):
        """
        Aggiorna il real_state della PCB con il nuovo observed_state.
        """
        self.real_state = observed_state

class Component:
    def __init__(self, idComponent, componentTypeName, state, defect_probabilities):
        self.idComponent = idComponent
        self.componentTypeName = componentTypeName
        self.state = state
        self.defect_probabilities = defect_probabilities


