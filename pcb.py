import random


class PCB:
    def __init__(self, idPCB, PCBTypeName, components, real_state = None):
        self.idPCB = idPCB
        self.PCBTypeName = PCBTypeName
        self.components = components
        self.initialize_real_state()
        self.current_profit = 0

    def initialize_real_state(self):
        for component in self.components:
            # Generate a random number between 0 and 1
            random_value = random.random()
            
            # Iterate through the defect probabilities and assign the state
            cumulative_probability = 0
            for defect, probability in component.state_probabilities.items():
                cumulative_probability += probability
                if random_value <= cumulative_probability:
                    component.state = defect
                    break

class Component:
    def __init__(self, idComponent, componentTypeName, state_probabilities):
        self.idComponent = idComponent
        self.componentTypeName = componentTypeName
        self.state = None #real state of component
        self.state_probabilities = state_probabilities #true probabilities of defects
        self.observed_state = state_probabilities #here you need to instantiate meanigfully, e.g. all defects equally probable {"solder": 0.99, "leg": 0.0, "burned": 0.0}


