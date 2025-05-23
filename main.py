#!/usr/bin/env python3

# main.py
from setup import setup_pcb, setup_measurements, setup_strategies, setup_actions
from simulation import pcb_process
from db_manager import DatabaseManager
from agent import DQNAgent
from decision_system import Decision_System
import simpy
import torch
from torch.utils.tensorboard import SummaryWriter
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables
import json
import shutil
import matplotlib.pyplot as plt
# Disable interactive mode globally
plt.ioff()


import io
# Load .env variables
load_dotenv()

def main_function():
    # Load parameters from .env
    NUM_EPISODES = int(os.getenv("NUM_EPISODES", 100))
    HIDDEN_DIM = int(os.getenv("HIDDEN_DIM", 64))
    TENSORBOARD_FLUSH_SECS = int(os.getenv("TENSORBOARD_FLUSH_SECS", 120))
    RUNS_DIR = os.getenv("RUNS_DIR", "runs")
    MAX_NUM_IMAGES  = int(os.getenv("MAX_NUM_IMAGES", 10))
    SMOOTHING_FACTOR = float(os.getenv("SMOOTHING_FACTOR", 0.1)) # Adjust the smoothing factor (0 < SMOOTHING_FACTOR ≤ 1)
    smoothed_profit = None  # Set to None initially      

    # Initialize SimPy environment and database manager
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Define the run directory structure
    run_dir = os.path.join(RUNS_DIR, f"run_{timestamp}")
    #tensorboard_dir = os.path.join(run_dir, "tb")
    model_dir = os.path.join(run_dir, "model")
    metadata_dir = os.path.join(run_dir, "startdata")

    # Create directories
    #os.makedirs(tensorboard_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)

    env = simpy.Environment()
    db = DatabaseManager(os.path.join(run_dir, f"db_{timestamp}.db"))
    #run_name = f"run_{timestamp}"
    writer = SummaryWriter(os.path.join("tensorb", f"run_{timestamp}"), flush_secs=TENSORBOARD_FLUSH_SECS)
    # Setup Measurements, Strategies, and Actions once
    measurements = setup_measurements()  # 'env' is now defined
    strategies = setup_strategies()
    actions = setup_actions(measurements, strategies)
    # Create a mapping from action index to action name
    action_idx_to_name = {idx: action.target.name for idx, action in enumerate(actions)}

    # Generate a sample PCB to determine node_feature_dim
    sample_pcb = setup_pcb()[0]
    node_feature_dim = len(sample_pcb.get_graph()[0][0])  # Number of features per node
    output_dim = len(actions)  # Total number of possible actions

    # Initialize the RL agent
    agent = DQNAgent(node_feature_dim, HIDDEN_DIM, output_dim, writer=writer)
    decision_system = Decision_System(agent, actions, None)  # Assuming no GNN model is needed here

    # Save metadata
    save_run_metadata(
        timestamp,
        agent,
        metadata_dir,
    )

    rewards = []
    stepsInLastEpisode = 0
    all_avg_rewards = []  # List of np.arrays

    # Calculate the intervals for image logging
    if MAX_NUM_IMAGES >= NUM_EPISODES:
        intervals = range(1, NUM_EPISODES + 1)  # Log every episode
    else:
        intervals = np.linspace(1, NUM_EPISODES, MAX_NUM_IMAGES, dtype=int)

    for episode in range(1, NUM_EPISODES + 1):        
        print(f"--- Starting Episode {episode} ---")
        
        agent.logging_data = {key: [] for key in agent.logging_data.keys()}
        agent.logging_data['action_rewards'] = {action: [] for action in range(output_dim)}

        progress = (episode - 1) / (NUM_EPISODES  - 1)  # 0 at start, 1 at last episode
        pcb_list = setup_pcb()  # Reset PCBs for each episode
        env = simpy.Environment()  # Reset environment for each episode
        # Initialize Measurements in the new environment
        for measurement in measurements:  # Assuming `measurements` is a list of `Measurement` instances
            measurement.initAsResourceInEnv(env)

        episode_rewards = []
        finished_pcb_list = []  # Initialize list to collect finished PCBs

        # Simulate each PCB
        for pcb in pcb_list:
            env.process(pcb_process(env, pcb, actions, db, decision_system, agent, episode_rewards, progress=progress, finished_pcb_list=finished_pcb_list))

        # Run the simulation
        env.run()

        # Aggregate rewards for the episode
        total_episode_reward = sum(episode_rewards)
        rewards.append(total_episode_reward)
        average_reward = np.mean(rewards[-10:])  # Average over last 10 episodes
        episode_profit = sum(pcb['total_profit'] for pcb in finished_pcb_list)
        print(f"--- Episode {episode} Completed: Total Reward = {total_episode_reward} | Average Reward = {average_reward:.2f} | Total profit = {episode_profit:.2f} ---")
        print(f"Number of PCBs Processed: {len(finished_pcb_list)}")
        
        # Log profit
        try:
            writer.add_scalar('total profit per episode', episode_profit, global_step=episode)
        except Exception as e:  
            print(f"An error occurred during logging: {e}")

        # Log rewards to TensorBoard
        # Calculate the average length of test_sequence
        try:
            total_length = sum(len(pcb['test_sequence']) for pcb in finished_pcb_list)
            average_length = total_length / len(finished_pcb_list) if finished_pcb_list else 0

            # Log the average length to TensorBoard
            writer.add_scalar('Average Test Sequence Length', average_length, global_step=episode)
        except Exception as e:  
            print(f"An error occurred during logging Average Test Sequence Length: {e}")

        # Calculate the average reward per test sequence length and plot
        try:
            if episode in intervals:
                avg_rewards = compute_avg_rewards(finished_pcb_list)
                all_avg_rewards.append(avg_rewards)
                plot_image = create_overlay_plot(all_avg_rewards, title=f"Avg Reward per Sequence Length up to Episode {episode}")
                plot_tensor = torch.tensor(plot_image).permute(2, 0, 1)
                writer.add_image('Average_Reward_Per_Sequence_Length', plot_tensor, global_step=episode, dataformats='CHW')
        except Exception as e:
            print(f"An error occurred during logging the overlay plot: {e}")

        try:
            writer.add_scalar('Total Reward per Episode', total_episode_reward, episode)
        except Exception as e:
            print(f"An error occurred during logging Total Reward per Episode: {e}")

        try:
            writer.add_scalar('Average Reward (Last 10 Episodes)', average_reward, episode)
        except Exception as e:
            print(f"An error occurred during logging Average Reward (Last 10 Episodes): {e}")

        # Log single rewards within the episode to TensorBoard
        for step, reward in enumerate(episode_rewards):
            try:
                writer.add_scalar(f'Reward per Step/Episode {episode}', reward, step)
            except Exception as e:
                print(f"An error occurred during logging Reward per Step/Episode {episode}: {e}")

        # Log average rewards per action using action names
        for action_idx, rewards_list in agent.logging_data['action_rewards'].items():
            if rewards_list:
                mean_reward = np.mean(rewards_list)
                action_name = action_idx_to_name.get(action_idx, f"Action_{action_idx}")
                try:
                    writer.add_scalar(f'Rewards/Action_{action_name}', mean_reward, episode)
                except Exception as e:
                    print(f"An error occurred during logging AverageActionRewardsPerEP/{action_name}: {e}")

        # Log epsilon per step
        for step, epsilon in enumerate(agent.logging_data['epsilon']):
            try:
                writer.add_scalar(f'Epsilon per Step', epsilon, step + stepsInLastEpisode)
            except Exception as e:
                print(f"An error occurred during logging Epsilon per Step: {e}")
        stepsInLastEpisode += len(agent.logging_data['epsilon'])


        # Log loss
        if agent.logging_data['loss']:
            mean_loss = np.mean(agent.logging_data['loss'])
            try:
                writer.add_scalar('Loss/train', mean_loss, episode)
            except Exception as e:
                print(f"An error occurred during logging Loss/train: {e}")

        # Log average Q-values
        if agent.logging_data['average_q']:
            mean_q = np.mean(agent.logging_data['average_q'])
            try:
                writer.add_scalar('Q-Values/Average Q-Value', mean_q, episode)
            except Exception as e:
                print(f"An error occurred during logging Q-Values/Average Q-Value: {e}")


        if smoothed_profit is None:
            # Initialize smoothed_profit with the first episode's profit
            smoothed_profit = episode_profit
        else:
            # Update the smoothed profit using a weighted average
            smoothed_profit = (
                SMOOTHING_FACTOR * episode_profit +
                (1 - SMOOTHING_FACTOR) * smoothed_profit
        )

        # # Log gradients
        # for name, grad in agent.logging_data['gradients']:
        #     try:
        #         writer.add_histogram(f'Gradients/{name}', grad, episode)
        #     except Exception as e:
        #         print(f"An error occurred during logging Gradients/{name}: {e}")

        # # Log weights
        # for name, weight in agent.logging_data['weights']:
        #     try:
        #         writer.add_histogram(f'Weights/{name}', weight, episode)
        #     except Exception as e:
        #         print(f"An error occurred during logging Weights/{name}: {e}")

        # Periodically update the target network
        if episode % 10 == 0:
            agent.update_target_network()        



    # After all episodes, close the database and TensorBoard writer
    writer.close()
    db.close()

    # Optionally, save the agent's model
    torch.save(agent.policy_net.state_dict(), os.path.join(model_dir, f"dqn_agent_{timestamp}.pth"))

    # Plot the learning curve
    #plot_learning_curve(rewards)
    return smoothed_profit


def save_run_metadata(timestamp, agent, output_dir, env_file=".env"):
    """
    Save run metadata, including environment variables, agent parameters, random states, and seed.

    Args:
        env (simpy.Environment): The simulation environment.
        agent (DQNAgent): The RL agent instance.
        random_state (tuple): Python random module's state.
        simpy_state (float): Current SimPy simulation time or seed.
        output_dir (str): Directory to save metadata files.
        env_file (str): Path to the .env file to be copied.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Copy .env file if it exists
    if os.path.exists(env_file):
        shutil.copy(env_file, os.path.join(output_dir, f"{os.path.basename(env_file)}"))
    else:
        print(f"Warning: {env_file} not found. Skipping .env file backup.")

    # Save agent parameters
    torch.save(agent.policy_net.state_dict(), os.path.join(output_dir, f"dqn_agent_{timestamp}.pth"))


def compute_avg_rewards(finished_pcb_list):
    """
    Computes the average reward for each sequence length in the finished_pcb_list.

    Args:
        finished_pcb_list (list of dict): Each dict should have 'test_sequence' and 'cumulative_reward' keys.

    Returns:
        dict: Mapping from sequence length to average reward.
    """
    length_rewards = {}
    for pcb in finished_pcb_list:
        length = len(pcb['test_sequence'])
        reward = pcb['cumulative_reward']
        if length not in length_rewards:
            length_rewards[length] = []
        length_rewards[length].append(reward)
    
    avg_rewards = {}
    for length, rewards in length_rewards.items():
        avg_rewards[length] = sum(rewards) / len(rewards)
    
    return avg_rewards

def create_overlay_plot(all_avg_rewards, title="Average Reward per Test Sequence Length", xlabel="Sequence Length", ylabel="Average Reward"):
    """
    Creates an overlay plot of average rewards per sequence length across episodes.

    Args:
        all_avg_rewards (list of dict): Each dict maps sequence lengths to average rewards.
        title (str): Title of the plot.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.

    Returns:
        np.ndarray: The plotted image as a NumPy array.
    """
    plt.figure(figsize=(10, 7))
    
    # Iterate over each dataset and plot it
    for idx, avg_rewards in enumerate(all_avg_rewards):
        # Sort the keys for consistent plotting
        sorted_lengths = sorted(avg_rewards.keys())
        sorted_rewards = [avg_rewards[length] for length in sorted_lengths]
        
        # Plot with a unique color and marker
        plt.plot(
            sorted_lengths, sorted_rewards, 
            marker='o', label=f'Dataset {idx+1}', alpha=0.7
        )
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc='best', fontsize='small', ncol=2)
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot to a PNG in memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    # Read the image from the buffer
    image = plt.imread(buf)
    
    return image


if __name__ == "__main__":
    main_function()
