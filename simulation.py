from decision_system import Decision_System

def pcb_process(env, pcb, actions, db):
    decision_system = Decision_System(actions, pcb)
    total_time = 0
    test_sequence = []

    print(f"[{env.now}] Starting process for PCB {pcb.idPCB}")

    while True:
        next_action = decision_system.select_next_action()
        #next action is executed; action executes with reference to measurement or strategy. 
        # but measurement is generic type, so inr eal you have an instance of a specific measurement where you call execute. 
        # All the changes to the pcb are done within execute

        
        if not next_action:
            print(f"[{env.now}] No more valid actions for PCB {pcb.idPCB}")
            break

        if next_action.action_type == "test":
            measurement = next_action.target
            print(f"[{env.now}] PCB {pcb.idPCB} waiting for measurement {measurement.name}")
            
            # Simulate the measurement
            # result = yield env.process(measurement.measure(env, pcb))
            
            # pcb.real_state = result.get("observed_state", pcb.real_state)
            pcb.current_profit -= result.get("cost", 0)

            test_sequence.append(measurement.name)
            total_time += measurement.duration

        elif next_action.action_type == "strategy":
            result = next_action.execute(pcb.real_state)
            pcb.current_profit += result.get("income", 0)

            print(f"[{env.now}] Strategy chosen: {next_action.target.name}")

            db.insert_test_result(
                ','.join(test_sequence),
                next_action.target.name if next_action.action_type == "strategy" else "NoStrategy",
                total_time,
                pcb.current_profit
            )
            break

    print(f"[{env.now}] Decision process completed for PCB {pcb.idPCB}")
