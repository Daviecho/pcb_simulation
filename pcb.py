# pcb.py
import random

class PCB:
    def __init__(self, idPCB, PCBTypeName, components):
        self.idPCB = idPCB
        self.PCBTypeName = PCBTypeName
        self.components = components
        self.initialize_real_state()
        self.current_profit = 0

    def initialize_real_state(self):
        for component in self.components:
            component.initialize_real_state()

    def get_graph(self):
        """
        Converts the PCB into a graph representation for GNN.
        Nodes represent components with features, edges can be based on PCB topology.
        """
        # For simplicity, assuming a fully connected graph
        nodes = []
        edges = []
        for component in self.components:
            nodes.append(component.get_features())

        num_nodes = len(self.components)
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                edges.append((i, j))
                edges.append((j, i))  # Assuming undirected edges

        return nodes, edges
    
    def clone(self):
        # Create a deep copy of the PCB
        cloned_components = [component.clone() for component in self.components]
        cloned_pcb = PCB(self.idPCB, self.PCBTypeName, cloned_components)
        cloned_pcb.current_profit = self.current_profit
        return cloned_pcb

class Component:
    def __init__(self, idComponent, componentTypeName, state_probabilities):
        self.idComponent = idComponent
        self.componentTypeName = componentTypeName
        self.state = None  # Real state of component
        self.state_probabilities = state_probabilities  # True probabilities of defects
        self.observed_state = {k: 0.5 for k in state_probabilities}  # Initialize with equal probabilities

    def initialize_real_state(self):
        random_value = random.random()
        cumulative_probability = 0
        for defect, probability in self.state_probabilities.items():
            cumulative_probability += probability
            if random_value <= cumulative_probability:
                self.state = defect
                break

    def get_features(self):
        """
        Returns feature vector for the component.
        Example features:
        - One-hot encoding of component type
        - One-hot encoding of observed defects
        """
        # For simplicity, assume componentTypeName is unique per type and mapped externally
        # Here, we return a placeholder vector
        # In practice, you would encode componentTypeName and observed_state into numerical features
        feature_vector = [self.idComponent]
        for defect, prob in self.observed_state.items():
            feature_vector.append(prob)
        return feature_vector
    
    def clone(self):
        # Create a deep copy of the Component
        cloned_component = Component(self.idComponent, self.componentTypeName, self.state_probabilities.copy())
        cloned_component.state = self.state
        cloned_component.observed_state = self.observed_state.copy()
        return cloned_component