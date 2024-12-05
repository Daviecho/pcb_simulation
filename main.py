from setup import setup_pcb, setup_measurements, setup_strategies
from simulation import pcb_process
from db_manager import DatabaseManager
import simpy

def main_function():
    env = simpy.Environment()
    db = DatabaseManager()

    # Setup PCB, Measurements, and Strategies
    pcb_list = setup_pcb()
    measurements = setup_measurements()
    strategies = setup_strategies()

    # Simulate each PCB
    for pcb in pcb_list:
        env.process(pcb_process(env, pcb, measurements, strategies, db))

    env.run()

if __name__ == "__main__":
    main_function()
