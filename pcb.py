class PCB:
    def __init__(self, idPCB, PCBTypeName, components):
        self.idPCB = idPCB
        self.PCBTypeName = PCBTypeName
        self.components = components

class Component:
    def __init__(self, idComponent, componentTypeName, state, defect_probabilities):
        self.idComponent = idComponent
        self.componentTypeName = componentTypeName
        self.state = state
        self.defect_probabilities = defect_probabilities
