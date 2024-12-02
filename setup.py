import random
from pcb import PCB, Component
from measurement import Measurement
from strategy import Strategy

def setup_pcb():
    """
    Crea una lista di PCB con componenti e probabilità di difetti generate casualmente.
    """
    pcb_list = []
    for i in range(3):  # Genera 3 PCB
        components = []  # Lista di componenti per questa PCB
        for j in range(random.randint(2, 5)):  # Ogni PCB ha da 2 a 5 componenti
            component = Component(
                idComponent=j + 1,
                defect_probabilities={
                    "solder": random.choice([0, 1]),
                    "leg": random.choice([0, 1]),
                    "burned": random.choice([0, 1])
                },
                componentTypeName=f"Type_{j + 1}",  # Nome generico del tipo
                state="noDefect"  # Stato iniziale predefinito
            )
            components.append(component)
        # Passa i componenti alla PCB
        pcb = PCB(i + 1, f"PCB_Type_{i + 1}", components)
        pcb_list.append(pcb)
    return pcb_list


def setup_measurements():
    """
    Crea una lista di test disponibili con accuratezze predefinite.
    """
    return [
        Measurement(1, "X-Ray", {"solder": 1.0, "leg": 1.0, "burned": 0.0}, duration=5, cost=10),
        Measurement(2, "Visual Inspection", {"solder": 0.0, "leg": 1.0, "burned": 0.0}, duration=3, cost=5),
        Measurement(3, "Flying Probe", {"solder": 1.0, "leg": 1.0, "burned": 1.0}, duration=7, cost=15)
    ]

def setup_strategies():
    return [
        Strategy(1, "Reuse", cost=20, income=100),
        Strategy(2, "Repair", cost=50, income=150),
        Strategy(3, "Recycle", cost=10, income=50),  # Strategia Recycle
    ]

