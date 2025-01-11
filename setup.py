# setup.py
import random
from pcb import PCB, Component
from measurement import Measurement  # Only one class now
from strategy import Strategy
from action import Action
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Load parameters from .env
NUM_PCBS = int(os.getenv("NUM_PCBS", 1000))
MIN_COMPONENTS = int(os.getenv("MIN_COMPONENTS", 3))
MAX_COMPONENTS = int(os.getenv("MAX_COMPONENTS", 10))


def generate_state_probabilities():
    """
    Generates a dictionary of defect probabilities that sum to 1.

    Returns:
        dict: A dictionary with keys 'solder', 'leg', 'burned', 'noDefect' and values summing to 1.
    """
    probs = [random.uniform(0, 1) for _ in range(4)]
    total = sum(probs)
    return {
        "solder": probs[0] / total,
        "leg": probs[1] / total,
        "burned": probs[2] / total,
        "noDefect": probs[3] / total
    }

def setup_pcb():
    """
    Sets up a list of 1,000 PCBs with randomized components and defect probabilities.

    Returns:
        list: A list of PCB instances.
    """
    pcb_list = []
    num_pcb = NUM_PCBS  # Total number of PCBs to generate
    min_components = MIN_COMPONENTS  # Minimum number of components per PCB
    max_components = MAX_COMPONENTS  # Maximum number of components per PCB

    # Define possible component types and PCB types
    component_types = ["Type_1", "Type_2", "Type_3", "Type_4", "Type_5"]
    pcb_types = [f"PCB_Type_{i}" for i in range(1, 11)]  # PCB_Type_1 to PCB_Type_10

    for i in range(1, num_pcb + 1):
        # Randomize the number of components for this PCB
        num_components = random.randint(min_components, max_components)
        components = []

        for j in range(1, num_components + 1):
            # Randomize component type
            component_type = random.choice(component_types)

            # Generate random defect probabilities
            state_probabilities = generate_state_probabilities()

            # Create a Component instance
            component = Component(
                idComponent=j,
                componentTypeName=component_type,
                state_probabilities=state_probabilities
            )
            components.append(component)

        # Randomize PCB type
        pcb_type = random.choice(pcb_types)

        # Create a PCB instance
        pcb = PCB(
            idPCB=i,
            PCBTypeName=pcb_type,
            components=components
        )
        pcb_list.append(pcb)

    return pcb_list



def parse_measurements():
    """
    Parses measurement configurations from .env and returns a list of Measurement instances.

    Returns:
        list: A list of Measurement instances.
    """
    measurements = []
    index = 1
    while True:
        # Attempt to load the next measurement configuration
        id_ = os.getenv(f"MEASUREMENT_{index}_ID")
        name = os.getenv(f"MEASUREMENT_{index}_NAME")
        solder = os.getenv(f"MEASUREMENT_{index}_SOLDER")
        leg = os.getenv(f"MEASUREMENT_{index}_LEG")
        burned = os.getenv(f"MEASUREMENT_{index}_BURNED")
        duration = os.getenv(f"MEASUREMENT_{index}_DURATION")
        cost = os.getenv(f"MEASUREMENT_{index}_COST")

        if not id_ or not name:  # Stop when no further measurements are found
            break

        # Create a Measurement instance
        detection_probs = {
            "solder": float(solder),
            "leg": float(leg),
            "burned": float(burned),
        }
        measurements.append(Measurement(int(id_), name, detection_probs, int(duration), int(cost)))

        index += 1  # Move to the next measurement

    return measurements

def parse_strategies():
    """
    Parses strategy configurations from .env and returns a list of Strategy instances.

    Returns:
        list: A list of Strategy instances.
    """
    strategies = []
    index = 1
    while True:
        # Attempt to load the next strategy configuration
        id_ = os.getenv(f"STRATEGY_{index}_ID")
        name = os.getenv(f"STRATEGY_{index}_NAME")
        cost = os.getenv(f"STRATEGY_{index}_COST")
        income = os.getenv(f"STRATEGY_{index}_INCOME")
        repair_cost = os.getenv(f"STRATEGY_{index}_REPAIR_COST")

        if not id_ or not name:  # Stop when no further strategies are found
            break

        # Create a Strategy instance
        strategies.append(Strategy(int(id_), name, int(cost), int(income), float(repair_cost) if repair_cost else None))

        index += 1  # Move to the next strategy

    return strategies


def setup_measurements():
    return parse_measurements()
    return [
        Measurement(
            1, 
            "X-Ray",
            {"solder": 0.9, "leg": 0.8, "burned": 0.7},
            duration=5, 
            cost=10
        ),
        Measurement(
            2, 
            "Visual Inspection",
            {"solder": 0.7, "leg": 0.6, "burned": 0.4},
            duration=3, 
            cost=5
        ),
        Measurement(
            3, 
            "Flying Probe",
            {"solder": 0.95, "leg": 0.9, "burned": 0.85},
            duration=7, 
            cost=15
        ),
    ]

def setup_strategies():
    return parse_strategies()
    return [
        Strategy(1, "Reuse", cost=20, income=100),    # Adjusted income to positive
        Strategy(2, "Repair", cost=5, income=150, repair_cost=3.0),   # Adjusted income to positive
        Strategy(3, "Recycle", cost=4, income=5)    # Adjusted income to positive
    ]

def setup_actions(measurements, strategies):
    # Measurements
    actions = [Action("test", measurement, measurement.cost, measurement.duration) for measurement in measurements]
    # Strategies
    actions += [Action("strategy", strategy, strategy.cost, 0) for strategy in strategies]
    return actions
