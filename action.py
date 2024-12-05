import random

class Action:
    def __init__(self, action_type, target, cost, duration):
        self.action_type = action_type  # "test" o "strategy"
        self.target = target
        self.cost = cost
        self.duration = duration

    def execute(self, real_state, pcb):
        if self.action_type == "test":
            # Chiama il metodo specifico per il test
            if self.target.name == "X-Ray":
                return self.xray(real_state)
            elif self.target.name == "Visual Inspection":
                return self.visual_inspection(real_state)
            elif self.target.name == "Flying Probe":
                return self.flying_probe(real_state)
        elif self.action_type == "strategy":
            return {"observed_state": real_state, "income": self.target.income - self.target.cost}

    def xray(self, real_state):
        """
        Metodo specifico per simulare l'azione di X-Ray.
        """
        observed_state = {}
        for component_id, defects in real_state.items():
            observed_state[component_id] = {}
            for defect_name, probability in defects.items():
                # Simula l'osservazione basata sull'accuratezza dell'X-Ray
                if random.random() < self.target.get_accuracy(defect_name):
                    # Aggiorna la probabilità aumentando la certezza sul difetto
                    observed_state[component_id][defect_name] = min(1.0, probability + random.uniform(0.1, 0.3))
                else:
                    # Diminuisce la probabilità se non rilevato
                    observed_state[component_id][defect_name] = max(0.0, probability - random.uniform(0.1, 0.2))
        return {"observed_state": observed_state}

    def visual_inspection(self, real_state):
        """
        Metodo specifico per simulare l'azione di Visual Inspection.
        """
        observed_state = {}
        for component_id, defects in real_state.items():
            observed_state[component_id] = {}
            for defect_name, probability in defects.items():
                # Simula l'osservazione basata sull'accuratezza della Visual Inspection
                if random.random() < self.target.get_accuracy(defect_name):
                    observed_state[component_id][defect_name] = min(1.0, probability + random.uniform(0.05, 0.2))
                else:
                    observed_state[component_id][defect_name] = max(0.0, probability - random.uniform(0.05, 0.1))
        return {"observed_state": observed_state}

    def flying_probe(self, real_state):
        """
        Metodo specifico per simulare l'azione di Flying Probe.
        """
        observed_state = {}
        for component_id, defects in real_state.items():
            observed_state[component_id] = {}
            for defect_name, probability in defects.items():
                # Simula l'osservazione basata sull'accuratezza del Flying Probe
                if random.random() < self.target.get_accuracy(defect_name):
                    observed_state[component_id][defect_name] = min(1.0, probability + random.uniform(0.15, 0.35))
                else:
                    observed_state[component_id][defect_name] = max(0.0, probability - random.uniform(0.1, 0.15))
        return {"observed_state": observed_state}
