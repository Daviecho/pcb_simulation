import random
import simpy


class Measurement:
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity=1):
        self.idMeasurement = idMeasurement
        self.name = nameMeasurement
        self.accuracy = accuracy
        self.duration = duration
        self.cost = cost
        self.resource = simpy.Resource(env, capacity=capacity)  # SimPy resource to manage concurrency
        self.queue = []  # Queue to track waiting PCBs
        self.env = env

    def get_accuracy(self, defect_name):
        return self.accuracy.get(defect_name, 0)

    def execute(self, pcb):
        with self.resource.request() as request:
            self.queue.append(pcb.idPCB)  # Add PCB to queue
            yield request  # Wait for the resource to become available
            self.queue.remove(pcb.idPCB)  # Remove PCB from queue

            # Simulate the measurement duration
            yield self.env.timeout(self.duration)

            # Update the observed state of each component based on real state and accuracy
            for component in pcb.components:
                real_state = component.state  # Real state of the component
                observed_state = component.observed_state  # Current observed state of the component

                # If the real state matches with probability based on accuracy, update the observed state
                if real_state and real_state != "no_defect":
                    detection_chance = self.get_accuracy(real_state)
                    if random.random() <= detection_chance:
                        observed_state = real_state

                component.observed_state = observed_state  # Update the component's observed state

            # Combine observed states for logging
            concatenated_states = ", ".join([f"{component.idComponent}: {component.observed_state}" for component in pcb.components])

            # Simulate the result of the measurement
            result = {
                "observed_state": concatenated_states,
                "cost": self.cost
            }

            print(f"[{self.env.now}] Measurement {self.name} completed for PCB {pcb.idPCB}")
            print(f"Observed State: {result['observed_state']}")
            return result
