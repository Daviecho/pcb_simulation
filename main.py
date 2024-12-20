from setup import setup_pcb, setup_measurements, setup_strategies, setup_actions
from simulation import pcb_process
from db_manager import DatabaseManager
import simpy

def main_function():
    env = simpy.Environment()
    db = DatabaseManager()

    # Setup PCB, Measurements, Strategies and actions
    pcb_list = setup_pcb()
    measurements = setup_measurements(env)
    strategies = setup_strategies()
    actions = setup_actions(measurements, strategies)

    # Simulate each PCB
    for pcb in pcb_list:
        env.process(pcb_process(env, pcb, actions, db))

    env.run()

if __name__ == "__main__":
    main_function()
