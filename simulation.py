import random
from pcb import PCB, Component
from measurement import Measurement
from decision_system import Decision_System
from strategy import strategy
from database import DatabaseManager

def pcb_process(env, db):
    """Simulates the processing of a PCB with variable data."""
    print(f"[{env.now}] Starting process for a new PCB")

    # Define fixed types of PCBs
    pcb_types = ["PCB_Type_1", "PCB_Type_2", "PCB_Type_3"]

    # Randomly select a type for the PCB
    pcb_type_name = random.choice(pcb_types)

    # Insert the PCB into the database and get its ID
    pcb_id = db.insert_pcb(pcb_type_name)
    pcb = PCB(pcb_id, pcb_type_name)

    # Generate a random number of components (e.g., between 2 and 5)
    num_components = random.randint(2, 5)
    for i in range(num_components):
        component_type = f"Component_Type_{random.randint(1, 3)}"
        component = Component(i + 1, "noDefect", component_type)

        # Assign random probabilities for defects
        component.set_defect_probability("solder", round(random.uniform(0, 0.8), 2))
        component.set_defect_probability("leg", round(random.uniform(0, 0.7), 2))
        component.set_defect_probability("burned", round(random.uniform(0, 0.6), 2))

        pcb.add_component(component)

    # Define measurements
    xRay = Measurement(1, "X-Ray")
    xRay.set_accuracy("solder", 1.0)
    xRay.set_accuracy("leg", 1.0)
    xRay.set_accuracy("burned", 0.0)
    xRay.cost = 50

    visualInspection = Measurement(2, "Visual Inspection")
    visualInspection.set_accuracy("solder", 0.0)
    visualInspection.set_accuracy("leg", 1.0)
    visualInspection.set_accuracy("burned", 0.0)
    visualInspection.cost = 30

    flyingProbe = Measurement(3, "Flying Probe")
    flyingProbe.set_accuracy("solder", 1.0)
    flyingProbe.set_accuracy("leg", 1.0)
    flyingProbe.set_accuracy("burned", 1.0)
    flyingProbe.cost = 70

    measurements = [xRay, visualInspection, flyingProbe]

    # Define strategies as objects
    strategies = [
        strategy("reuse", random.randint(40, 60), random.randint(100, 160)),
        strategy("recycle", random.randint(60, 80), random.randint(150, 210)),
        strategy("repair", random.randint(90, 120), random.randint(250, 320))
    ]

    # Decision System to calculate the best test sequence and strategy
    decision_system = Decision_System(measurements, pcb, strategies)
    best_sequence, best_strategy = decision_system.select_best_strategy()

    # Calculate costs, income, and profit
    sequence_cost = sum(test.cost for test in best_sequence)
    sequence_income = best_strategy.income
    profit = sequence_income - sequence_cost

    # Save results in the database
    test_sequence = ", ".join([test.nameMeasurement for test in best_sequence])
    db.insert_test_result(pcb.idPCB, test_sequence, best_strategy.name, sequence_cost, sequence_income, profit)

    # Save component probabilities
    for component in pcb.components:
        for defect_name, probability in component.defect_probabilities.items():
            db.insert_probabilities(pcb.idPCB, component.idComponent, defect_name, probability)

    print(f"[{env.now}] PCB {pcb_id} completed. Strategy: {best_strategy.name}, Profit: {profit}")
    yield env.timeout(1)
