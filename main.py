# main.py
from setup import setup_pcb, setup_measurements, setup_strategies, setup_actions
from simulation import pcb_process
from db_manager import DatabaseManager
from agent import DQNAgent
from decision_system import Decision_System
import simpy
import torch
import matplotlib.pyplot as plt
from torch.utils.tensorboard import SummaryWriter
import numpy as np
from datetime import datetime
import os

def plot_learning_curve(rewards, window=100):
    """
    Plots the learning curve using the cumulative rewards.
    
    Args:
        rewards (list): List of cumulative rewards per episode.
        window (int): Window size for moving average.
    """
    rewards = np.array(rewards)
    moving_average = np.convolve(rewards, np.ones(window)/window, mode='valid')

    plt.figure(figsize=(12, 6))
    plt.plot(rewards, label='Total Reward per Episode', alpha=0.5)
    plt.plot(moving_average, label=f'Moving Average (window={window})', color='red')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('RL Agent Learning Progress Over Episodes')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('learning_curve.png')  # Save the plot as a PNG file
    plt.show()

def main_function():
    # Initialize SimPy environment and database manager
    env = simpy.Environment()
    db = DatabaseManager()
    run_name = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    writer = SummaryWriter(os.path.join('runs', run_name))

    # Setup Measurements, Strategies, and Actions once
    measurements = setup_measurements(env)  # 'env' is now defined
    strategies = setup_strategies()
    actions = setup_actions(measurements, strategies)

    # Generate a sample PCB to determine node_feature_dim
    sample_pcb = setup_pcb()[0]
    node_feature_dim = len(sample_pcb.get_graph()[0][0])  # Number of features per node
    hidden_dim = 64
    output_dim = len(actions)  # Total number of possible actions

    # Initialize the RL agent
    agent = DQNAgent(node_feature_dim, hidden_dim, output_dim, writer=writer)
    decision_system = Decision_System(agent, actions, None)  # Assuming no GNN model is needed here

    num_episodes = 100  # Define number of training episodes
    rewards = []

    for episode in range(1, num_episodes + 1):
        print(f"--- Starting Episode {episode} ---")
        pcb_list = setup_pcb()  # Reset PCBs for each episode
        env = simpy.Environment()  # Reset environment for each episode
        episode_rewards = []

        # Simulate each PCB
        for pcb in pcb_list:
            env.process(pcb_process(env, pcb, actions, db, decision_system, agent, episode_rewards))

        # Run the simulation
        env.run()

        # Aggregate rewards for the episode
        total_episode_reward = sum(episode_rewards)
        rewards.append(total_episode_reward)
        average_reward = np.mean(rewards[-10:])  # Average over last 10 episodes
        print(f"--- Episode {episode} Completed: Total Reward = {total_episode_reward} | Average Reward = {average_reward:.2f} ---")

        # Log rewards to TensorBoard
        writer.add_scalar('Total Reward per Episode', total_episode_reward, episode)
        writer.add_scalar('Average Reward (Last 10 Episodes)', average_reward, episode)

        # Periodically update the target network
        if episode % 10 == 0:
            agent.update_target_network()

    # After all episodes, close the database and TensorBoard writer
    db.close()
    writer.close()

    # Optionally, save the agent's model
    torch.save(agent.policy_net.state_dict(), "dqn_agent.pth")

    # Plot the learning curve
    #plot_learning_curve(rewards)

if __name__ == "__main__":
    main_function()
