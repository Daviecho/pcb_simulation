from decision_system import Decision_System

def pcb_process(env, pcb, measurements, strategies, db):
    decision_system = Decision_System(measurements, strategies, pcb)
    print(f"[{env.now}] Starting process for PCB {pcb.idPCB}")

    test_sequence = []
    total_time = 0
    chosen_strategy = None

    while True:
        next_action = decision_system.select_next_action()
        if not next_action:
            print("[Error] No valid action found!")
            break

        if next_action.action_type == "test":
            result = next_action.execute(decision_system.observed_state, pcb)
            decision_system.update_observed_state(result["observed_state"])
            test_sequence.append(next_action.target.name)
            yield env.timeout(next_action.duration)
            total_time += next_action.duration

        elif next_action.action_type == "strategy":
            chosen_strategy = next_action.target.name
            break

    db.insert_test_result(
        pcb.idPCB,
        ','.join(test_sequence),
        chosen_strategy,
        total_time,
        decision_system.calculate_decision_value(next_action)
    )
    print(f"[{env.now}] Results saved for PCB {pcb.idPCB}")
