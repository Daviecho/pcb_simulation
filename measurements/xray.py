from measurement import Measurement

class XRay(Measurement):
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity=1):
        super().__init__(idMeasurement, nameMeasurement, accuracy, duration, cost, env, capacity)

    def execute(self, pcb):
        for component in pcb.components:
            if component.state == "leg":
                # Update observed state probabilities for "leg" to 0.99
                component.state_probabilities["leg"] = 0.99
        print(f"XRay executed on PCB {pcb.idPCB}. Observed state updated where applicable.")
