# measurement.py
import random
import simpy

class Measurement:
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity=1):
        self.idMeasurement = idMeasurement
        self.name = nameMeasurement
        self.accuracy = accuracy  # Dict of defect_name: accuracy
        self.duration = duration
        self.cost = cost
        self.resource = simpy.Resource(env, capacity=capacity)  # SimPy resource to manage concurrency
        self.env = env

    def get_accuracy(self, defect_name):
        return self.accuracy.get(defect_name, 0)

    def execute(self, pcb):
        """
        Executes the measurement on the PCB.
        Returns observed state and cost.
        """
        # This method will be overridden by subclasses if needed
        raise NotImplementedError("Execute method must be implemented by subclasses.")

class XRay(Measurement):
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity=1):
        super().__init__(idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity)

    def execute(self, pcb):
        with self.resource.request() as request:
            yield request  # Wait for resource
            yield self.env.timeout(self.duration)  # Simulate measurement duration

            observed_state = {}
            for component in pcb.components:
                for defect, prob in component.state_probabilities.items():
                    if component.state == defect:
                        if random.random() < self.get_accuracy(defect):
                            observed_state[component.idComponent] = defect
                    else:
                        # False positive handling can be implemented here
                        pass  # For simplicity, ignoring false positives

            # Update PCB's observed state based on measurement
            for component in pcb.components:
                if component.idComponent in observed_state:
                    component.observed_state = {k: 0.0 for k in component.observed_state}
                    component.observed_state[observed_state[component.idComponent]] = 1.0

            result = {
                "observed_state": observed_state,
                "cost": self.cost
            }

            print(f"[{self.env.now}] X-Ray Measurement completed for PCB {pcb.idPCB}")
            return result

class VisualInspection(Measurement):
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity=1):
        super().__init__(idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity)

    def execute(self, pcb):
        with self.resource.request() as request:
            yield request
            yield self.env.timeout(self.duration)

            observed_state = {}
            for component in pcb.components:
                for defect, prob in component.state_probabilities.items():
                    if component.state == defect:
                        if random.random() < self.get_accuracy(defect):
                            observed_state[component.idComponent] = defect
                    else:
                        pass  # Ignoring false positives for simplicity

            for component in pcb.components:
                if component.idComponent in observed_state:
                    component.observed_state = {k: 0.0 for k in component.observed_state}
                    component.observed_state[observed_state[component.idComponent]] = 1.0

            result = {
                "observed_state": observed_state,
                "cost": self.cost
            }

            print(f"[{self.env.now}] Visual Inspection completed for PCB {pcb.idPCB}")
            return result

class FlyingProbe(Measurement):
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity=1):
        super().__init__(idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity)

    def execute(self, pcb):
        with self.resource.request() as request:
            yield request
            yield self.env.timeout(self.duration)

            observed_state = {}
            for component in pcb.components:
                for defect, prob in component.state_probabilities.items():
                    if component.state == defect:
                        if random.random() < self.get_accuracy(defect):
                            observed_state[component.idComponent] = defect
                    else:
                        pass  # Ignoring false positives for simplicity

            for component in pcb.components:
                if component.idComponent in observed_state:
                    component.observed_state = {k: 0.0 for k in component.observed_state}
                    component.observed_state[observed_state[component.idComponent]] = 1.0

            result = {
                "observed_state": observed_state,
                "cost": self.cost
            }

            print(f"[{self.env.now}] Flying Probe Measurement completed for PCB {pcb.idPCB}")
            return result
