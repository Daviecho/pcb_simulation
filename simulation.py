from decision_system import Decision_System

def pcb_process(env, pcb, actions, db):
    """
    Processo per analizzare una PCB con la Decision_System.
    """
    decision_system = Decision_System(actions, pcb)
    total_time = 0
    test_sequence = []

    print(f"[{env.now}] Starting process for PCB {pcb.idPCB}")

    
    while True:
        next_action = decision_system.select_next_action()
        if not next_action:
            print(f"[{env.now}] No more valid actions for PCB {pcb.idPCB}")
            break

        if next_action.action_type == "test":
            result = next_action.execute(decision_system.observed_state, pcb)
            decision_system.update_observed_state(result["observed_state"])
            test_sequence.append(next_action.target.name)
            yield env.timeout(next_action.duration)
            total_time += next_action.duration

        elif next_action.action_type == "strategy":
            print(f"[{env.now}] Strategy chosen: {next_action.target.name}")
            db.insert_test_result(
                ','.join(test_sequence),  # La sequenza dei test eseguiti
                next_action.target.name if next_action.action_type == "strategy" else "NoStrategy",  # Strategia scelta o "NoStrategy"
                total_time,  # Tempo totale impiegato
                next_action.target.income - next_action.target.cost  # Profitto netto
            )

            break

    print(f"[{env.now}] Decision process completed for PCB {pcb.idPCB}")
