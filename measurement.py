import random
import simpy

class Measurement:
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost, capacity=1):
        self.idMeasurement = idMeasurement
        self.name = nameMeasurement
        self.accuracy = accuracy  # Dict of defect_name -> detection probability
        self.duration = duration
        self.cost = cost
        self.env = None
        self.capacity = capacity

    def initAsResourceInEnv(self, env):
        self.resource = simpy.Resource(env, capacity=self.capacity)
        self.env = env
        

    def get_accuracy(self, defect_name):
        return self.accuracy.get(defect_name, 0)

    def partial_update_observed_state(self, component, detected_defect, alpha=0.3):
        """
        Moves the component's observed_state probabilities slightly toward 'detected_defect'
        if we detect something, or leaves them if we detect nothing.
        """
        if detected_defect:
            # Shift probability distribution
            for defect in component.observed_state.keys():
                if defect == detected_defect:
                    component.observed_state[defect] = min(
                        1.0, component.observed_state[defect] + alpha
                    )
                else:
                    component.observed_state[defect] = max(
                        0.0,
                        component.observed_state[defect] - alpha / (len(component.observed_state) - 1)
                    )

    def log_observed_state(self, pcb, component, old_probs, real_defect, detected_defect):
        """
        Console logging to show how partial_update_observed_state() changed probabilities.
        """
        print(f"[{self.env.now}] {self.name} on PCB {pcb.idPCB}, Component {component.idComponent}")
        print(f"    Real Defect={real_defect}, Detected={detected_defect}")
        print(f"    Old ObservedState={old_probs}")
        print(f"    New ObservedState={component.observed_state}")

    def detect_defect(self, component):
        """
        A simple detection logic: If random < accuracy(real_defect), detect the real defect; else None.
        False positives could be added if desired.
        """
        real_defect = component.state
        if random.random() < self.get_accuracy(real_defect):
            return real_defect
        else:
            return None

    def do_measurement(self, pcb):
        with self.resource.request() as request:
            yield request
            yield self.env.timeout(self.duration)

            for component in pcb.components:
                # old_probs = dict(component.observed_state)  # snapshot before update
                # real_defect = component.state
                detected_defect = self.detect_defect(component)
                self.partial_update_observed_state(component, detected_defect)
                #self.log_observed_state(pcb, component, old_probs, real_defect, detected_defect)

        return {
            "observed_state": None,
            "cost": self.cost
        }

    def execute(self, pcb):
        # The actual measurement routine
        res = yield from self.do_measurement(pcb)
        return res
