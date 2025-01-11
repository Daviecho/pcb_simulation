# simulation.py
import simpy
from decision_system import Decision_System
from agent import DQNAgent
import random
import torch
import json
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Load test_bonus parameters
test_bonus_start = float(os.getenv("TEST_BONUS_START", 25))
test_bonus_zero_progress = float(os.getenv("TEST_BONUS_ZERO_PROGRESS", 0.5))
test_bonus_end = float(os.getenv("TEST_BONUS_END", -5))
test_bonus_end_progress = float(os.getenv("TEST_BONUS_END_PROGRESS", 1.0))

# Load recycle_bonus parameters
recycle_bonus_start = float(os.getenv("RECYCLE_BONUS_START", -5))
recycle_bonus_zero_progress = float(os.getenv("RECYCLE_BONUS_ZERO_PROGRESS", 0.4))
recycle_bonus_end = float(os.getenv("RECYCLE_BONUS_END", 10))
recycle_bonus_end_progress = float(os.getenv("RECYCLE_BONUS_END_PROGRESS", 0.8))

# Load repair_bonus parameters
repair_bonus_start = float(os.getenv("REPAIR_BONUS_START", -5))
repair_bonus_zero_progress = float(os.getenv("REPAIR_BONUS_ZERO_PROGRESS", 0.4))
repair_bonus_end = float(os.getenv("REPAIR_BONUS_END", 10))
repair_bonus_end_progress = float(os.getenv("REPAIR_BONUS_END_PROGRESS", 0.8))

# Load reuse_bonus parameters
reuse_bonus_start = float(os.getenv("REUSE_BONUS_START", -5))
reuse_bonus_zero_progress = float(os.getenv("REUSE_BONUS_ZERO_PROGRESS", 0.4))
reuse_bonus_end = float(os.getenv("REUSE_BONUS_END", 10))
reuse_bonus_end_progress = float(os.getenv("REUSE_BONUS_END_PROGRESS", 0.8))



def pcb_process(env, pcb, actions, db, decision_system, agent, rewards, max_actions=100, progress=0.0, finished_pcb_list=None):
    total_time = 0
    test_sequence = []
    done = False
    cumulative_reward = 0

    #endprogress > zeroprogress > 0
    test_bonus = linear_function(progress, test_bonus_start, test_bonus_zero_progress, test_bonus_end, test_bonus_end_progress)
    recycle_bonus = linear_function(progress, recycle_bonus_start, recycle_bonus_zero_progress, recycle_bonus_end, recycle_bonus_end_progress)
    repair_bonus = linear_function(progress, repair_bonus_start, repair_bonus_zero_progress, repair_bonus_end, repair_bonus_end_progress)
    reuse_bonus = linear_function(progress, reuse_bonus_start, reuse_bonus_zero_progress, reuse_bonus_end, reuse_bonus_end_progress)
    # (1 - progress) * 25 + progress * (-5)      # Great early, negative later
    # #recycle_bonus = (1 - progress) * (-5) #+ progress * 1   # Bad early, neutral later
    #repair_bonus = (1 - progress) * 0 + progress * 0       # No penalty for failed repairs


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
                reward = recycle_bonus
            elif action.target.name == "Repair":
                reward = result.get("income", 0) + repair_bonus
            elif action.target.name == "Reuse":
                reward = result.get("income", 0) + reuse_bonus
            else: #should never be hit currently
                # Reuse or other strategies
                reward = result.get("income", 0)

            pcb.current_profit += result.get("income", 0)
            done = True
        else:
            cost = result.get("cost", 0)
            pcb.current_profit -= cost 
            reward = test_bonus


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


def linear_function(progress, start_point, zero_progress, end_value, end_progress):
    """
    Computes the value of a linear function based on progress and the given parameters,
    with rules to validate inputs.

    Args:
        progress (float): The current progress value.
        start_point (float): The function value at progress = 0.
        zero_progress (float): The progress value when the function becomes zero.
        end_value (float): The function value at progress = end_progress.
        end_progress (float): The progress value when the function reaches end_value.

    Returns:
        float: The computed value of the function at the given progress.

    Raises:
        ValueError: If any input parameter violates the rules.
    """
    # Rule 1: zero_progress must be greater than 0
    if zero_progress <= 0:
        raise ValueError("zero_progress must be greater than 0.")

    # Rule 2: end_progress must be greater than zero_progress
    if end_progress <= zero_progress:
        raise ValueError("end_progress must be greater than zero_progress.")

    # Rule 3: progress must be non-negative
    if progress < 0:
        raise ValueError("progress cannot be negative.")

    # Compute the function value based on progress
    if progress <= zero_progress:
        # Linear interpolation from start_point to 0
        return start_point * (1 - (progress / zero_progress))
    elif zero_progress < progress <= end_progress:
        # Linear interpolation from 0 to end_value
        return end_value * ((progress - zero_progress) / (end_progress - zero_progress))
    else:
        # If progress exceeds end_progress, return the end_value
        return end_value