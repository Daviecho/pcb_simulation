from simulation import pcb_process
from setup import setup_pcb, setup_measurements, setup_strategies
from db_manager import DatabaseManager
import simpy

def main_function():
    # Database setup
    db = DatabaseManager("pcb_simulation.db")

    # Initial setup
    pcb_list = setup_pcb()
    measurements = setup_measurements()
    strategies = setup_strategies()

    #create actions here! or call an action to cretae all possible actions
    

    # Simulation environment
    env = simpy.Environment()

    # Process for each PCB
    for pcb in pcb_list:
        env.process(pcb_process(env, pcb, measurements, strategies, db))

    # Simulation run
    env.run()

if __name__ == "__main__":
    main_function()
