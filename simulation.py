# simulation.py
import simpy
from decision_system import Decision_System
from agent import DQNAgent
import random
import torch
import json

def pcb_process(env, pcb, actions, db, decision_system, agent, rewards, max_actions=100, progress=0.0, finished_pcb_list=None):
    total_time = 0
    test_sequence = []
    done = False
    cumulative_reward = 0

    test_bonus = (1 - progress) * 25 + progress * (-5)      # Great early, negative later
    recycle_bonus = (1 - progress) * (-5) #+ progress * 1   # Bad early, neutral later
    repair_bonus = (1 - progress) * 0 + progress * 0       # No penalty for failed repairs


    while not done:
        # Determine available actions
        available_actions = []
        # Avoid repeating the same measurement
        executed_tests = [action.target.name for action in actions if action.action_type == "test" and action.target.name in test_sequence]
        for idx, action in enumerate(actions): #currently a measurement can only be done once! Maybe we should 
            if action.action_type == "test" and action.target.name in executed_tests:
                continue
            available_actions.append(idx)

        # Select a test action using the agent
        action_idx = decision_system.select_next_action(pcb, available_actions)
        action = actions[action_idx]
        test_sequence.append(action.target.name)
        available_actions.remove(action_idx)

        state = pcb.clone()

        # Execute the test
        print(f"[{env.now}] PCB {pcb.idPCB} executing action {action.target.name}")
        result = yield env.process(action.execute(pcb, env))

        # Update profit
        reward = 0
        total_time += action.duration
        if action.action_type == "strategy":
            # Strategy action
            if action.target.name == "Recycle":
                # Income plus dynamic bonus
                reward = result.get("income", 0) + recycle_bonus
            elif action.target.name == "Repair":
                reward = result.get("income", 0) + repair_bonus
            else:
                # Reuse or other strategies
                reward = result.get("income", 0)

            pcb.current_profit += result.get("income", 0)
            done = True
        else:
            cost = result.get("cost", 0)
            pcb.current_profit -= cost 
            reward = test_bonus - cost


        # For RL, collect transition and store in replay buffer
        # Define reward as profit change
        # Since profit is updated, define reward accordingly
        # Here, as a simple example, reward is profit after action - previous profit

        # In practice, more sophisticated reward shaping can be applied
        # For demonstration, using -cost as immediate reward
        cumulative_reward += reward
        next_state = pcb.clone()
        done_flag = done
        agent.replay_buffer.push(state, action_idx, reward, next_state, done_flag)
        
        # Optimize the agent
        agent.optimize_model()
        rewards.append(cumulative_reward)

        # Print final log for this PCB

        # Append to finished_pcb_list if provided


    db.insert_test_result(
        pcb.idPCB,
        ','.join(test_sequence),
        total_time,
        pcb.current_profit,
        cumulative_reward,
        json.dumps({comp.idComponent: comp.state for comp in pcb.components}),
        json.dumps({comp.idComponent: comp.observed_state for comp in pcb.components})
)


    if finished_pcb_list is not None:
        finished_pcb_list.append({
            'idPCB': pcb.idPCB,
            'test_sequence': test_sequence,
            'cumulative_reward': cumulative_reward,
            'total_profit': pcb.current_profit
        })

    print(
        f"[{env.now}] PCB {pcb.idPCB} processing completed.\n"
        f"    Test Sequence: {test_sequence}\n"
        f"    Final Cumulative Reward: {cumulative_reward}\n"
        f"    Total Profit: {pcb.current_profit}")
    return cumulative_reward
