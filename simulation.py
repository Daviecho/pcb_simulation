import json
from decision_system import Decision_System

def pcb_process(env, pcb, measurements, strategies, db):
    decision_system = Decision_System(measurements, pcb, strategies)
    total_time = 0

    print(f"[{env.now}] Starting process for PCB {pcb.idPCB}")
    
    # Iterazione per il processo decisionale
    while True:
        result = decision_system.process_decision()  # Ottiene un'azione alla volta

        # Se è stata scelta una strategia, termina il processo
        if result["strategy"] is not None:
            print(f"[{env.now}] Strategy chosen: {result['strategy']}")
            total_time += sum([m.duration for m in measurements if m.nameMeasurement in result["test_sequence"]])
            break

        # Esegui l'azione restituita (un test)
        action = result["action"]
        print(f"[{env.now}] Executed test: {action.target.name}")
        yield env.timeout(action.duration)  # Simula il ritardo del test

    # Salva i risultati nel database
    db.insert_test_result(
        pcb.idPCB,
        ','.join(result["test_sequence"]),
        result["strategy"],
        total_time,
        result["income"]
    )
    print(f"[{env.now}] Results saved for PCB {pcb.idPCB}")
