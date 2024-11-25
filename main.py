from simulation import pcb_process
from database import DatabaseManager
import simpy

def main_function():
    import simpy
    from database import DatabaseManager
    from simulation import pcb_process

    db = DatabaseManager()
    env = simpy.Environment()

    # Launch processes for multiple PCBs
    for _ in range(3):  # Simulate 3 PCBs
        env.process(pcb_process(env, db))

    env.run()
    print("Simulation completed. Data has been saved to the database.")

if __name__ == "__main__":
    main_function()
