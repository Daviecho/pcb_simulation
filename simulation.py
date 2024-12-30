# simulation.py
import simpy
from decision_system import Decision_System
from agent import DQNAgent
import random
import torch

def pcb_process(env, pcb, actions, db, decision_system, agent, device, rewards, max_actions=100):
    total_time = 0
    test_sequence = []
    done = False
    cumulative_reward = 0
    while not done:
        # Determine available actions
        available_actions = []
        # Avoid repeating the same measurement
        executed_tests = [action.target.name for action in actions if action.action_type == "test" and action.target.name in test_sequence]
        for idx, action in enumerate(actions):
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
            pcb.current_profit += result.get("income", 0)
            db.insert_test_result(
                    ','.join(test_sequence),
                    action.target.name,
                    total_time,
                    pcb.current_profit
                )
            done = True
            reward = result.get("income", 0)
        else:
            pcb.current_profit -= result.get("cost", 0)   
            reward = -result.get("cost", 0)       


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

    print(f"[{env.now}] PCB {pcb.idPCB} processing completed. Total Profit: {pcb.current_profit}")
    return cumulative_reward
