from pcb import PCB, Component
from measurement import Measurement
from strategy import Strategy
from action import Action

# Creating 3 PCBs with 5 components each
def setup_pcb():
    pcb_list = []
    for i in range(3):  
        components = [
            Component(
                idComponent=j + 1,
                componentTypeName=f"Type_{j + 1}",
                state="noDefect",
                defect_probabilities={"solder": 0.5, "leg": 0.3, "burned": 0.2}
            )
            for j in range(5)
        ]  
        pcb = PCB(i + 1, f"PCB_Type_{i + 1}", components)
        pcb_list.append(pcb)
    return pcb_list

# Creating 3 measurements, specifying the accuracy for each kind of issue
def setup_measurements():
    return [
        Measurement(1, "X-Ray", {"solder": 0.9, "leg": 0.8, "burned": 0.7}, duration=5, cost=10),
        Measurement(2, "Visual Inspection", {"solder": 0.7, "leg": 0.6, "burned": 0.4}, duration=3, cost=5),
        Measurement(3, "Flying Probe", {"solder": 0.95, "leg": 0.9, "burned": 0.85}, duration=7, cost=15)
    ]


def setup_strategies():
    return [
        Strategy(1, "Reuse", cost=20, income=-100),
        Strategy(2, "Repair", cost=40, income=-150),
        Strategy(3, "Recycle", cost=10, income=-50)
    ]

# Creating the actions as a list comprohension (cointaining both measurements and strategies)
def setup_actions(measurements, strategies):
    actions = [
        Action("test", measurement, measurement.cost, measurement.duration) for measurement in measurements
    ] + [
        Action("strategy", strategy, strategy.cost, 0) for strategy in strategies
    ]
    return actions