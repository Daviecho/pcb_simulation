from decision_system import Decision_System

def pcb_process(env, pcb, actions, db):
    # Creating the decision system giving actions and the pcb
    decision_system = Decision_System(actions, pcb)
    total_time = 0

    test_sequence = []

    print(f"[{env.now}] Starting process for PCB {pcb.idPCB}")

    # Execute actions iteratively until a strategy is chosen or no valid actions remain
    while True:
        # Decision system gives the next action based on the real_state of the pcb
        # The real_state is available through the class pcb, containing always the last "state" version 
        next_action = decision_system.select_next_action()
        if not next_action:
            print(f"[{env.now}] No more valid actions for PCB {pcb.idPCB}")
            break

        if next_action.action_type == "test":
            # Simulation of test execution
            result = next_action.execute(pcb.real_state)

            # Updating the real_state after the execution information
            pcb.real_state = result.get("observed_state", pcb.real_state)

            # Updating profit after measurement cost 
            pcb.current_profit -= result.get("cost", pcb.real_state)

            test_sequence.append(next_action.target.name)
            yield env.timeout(next_action.duration)
            total_time += next_action.duration

        elif next_action.action_type == "strategy":
            # Simulation of strategy execution
            result = next_action.execute(pcb.real_state)

            # Updating profit after strategy income 
            pcb.current_profit += result.get("income", pcb.real_state)
            
            print(f"[{env.now}] Strategy chosen: {next_action.target.name}")

            db.insert_test_result(
                ','.join(test_sequence),  # La sequenza dei test eseguiti
                next_action.target.name if next_action.action_type == "strategy" else "NoStrategy",  # Strategia scelta o "NoStrategy"
                total_time,  # Tempo totale impiegato
                pcb.current_profit  # Profitto netto
            )
            break

    print(f"[{env.now}] Decision process completed for PCB {pcb.idPCB}")
    yield env.timeout(total_time)
