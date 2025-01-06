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
    writer = SummaryWriter(os.path.join('runs', run_name), flush_secs=120)    
    # Setup Measurements, Strategies, and Actions once
    measurements = setup_measurements()  # 'env' is now defined
    strategies = setup_strategies()
    actions = setup_actions(measurements, strategies)
    # Create a mapping from action index to action name
    action_idx_to_name = {idx: action.target.name for idx, action in enumerate(actions)}

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
    stepsInLastEpisode = 0

    for episode in range(1, num_episodes + 1):        
        print(f"--- Starting Episode {episode} ---")
        
        agent.logging_data = {key: [] for key in agent.logging_data.keys()}
        agent.logging_data['action_rewards'] = {action: [] for action in range(output_dim)}

        progress = (episode - 1) / (num_episodes - 1)  # 0 at start, 1 at last episode
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
        print(f"--- Episode {episode} Completed: Total Reward = {total_episode_reward} | Average Reward = {average_reward:.2f} ---")
        print(f"Number of PCBs Processed: {len(finished_pcb_list)}")

        # Log rewards to TensorBoard

        # Calculate the average length of test_sequence
        try:
            total_length = sum(len(pcb['test_sequence']) for pcb in finished_pcb_list)
            average_length = total_length / len(finished_pcb_list) if finished_pcb_list else 0

            # Log the average length to TensorBoard
            writer.add_scalar('Average Test Sequence Length', average_length, global_step=1)
        except Exception as e:
            print(f"An error occurred during logging Average Test Sequence Length: {e}")

        # Maximum sequence length
        max_length = 4

        # Calculate the average reward per test sequence length
        try:
            # Group rewards by test sequence length
            length_rewards = {}
            for pcb in finished_pcb_list:
                length = len(pcb['test_sequence'])
                reward = pcb['reward']
                if length not in length_rewards:
                    length_rewards[length] = []
                length_rewards[length].append(reward)
            
            # Create a fixed-size array for average rewards (size = max_length)
            avg_rewards = np.zeros(max_length)
            for length in range(1, max_length + 1):
                if length in length_rewards:
                    avg_rewards[length - 1] = sum(length_rewards[length]) / len(length_rewards[length])
                else:
                    avg_rewards[length - 1] = 0  # Or use np.nan for missing lengths

            # Log the array as a histogram for this episode
            writer.add_histogram('Average Reward per Test Sequence Length', avg_rewards, global_step=episode)
        except Exception as e:
            print(f"An error occurred during logging Average Reward per Test Sequence Length: {e}")

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
                    print(f"An error occurred during logging Rewards/Action_{action_name}: {e}")

        # Log epsilon per step
        for step, epsilon in enumerate(agent.logging_data['epsilon']):
            try:
                writer.add_scalar(f'Epsilon per Step', epsilon, step + stepsInLastEpisode)
            except Exception as e:
                print(f"An error occurred during logging Epsilon per Step: {e}")
        stepsInLastEpisode += len(agent.logging_data['epsilon'])

        # Log mean epsilon per episode
        if agent.logging_data['epsilon']:
            mean_epsilon = np.mean(agent.logging_data['epsilon'])
            try:
                writer.add_scalar(f'Mean Epsilon/Episode {episode}', mean_epsilon, episode)
            except Exception as e:
                print(f"An error occurred during logging Mean Epsilon/Episode {episode}: {e}")

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

        # Log gradients
        for name, grad in agent.logging_data['gradients']:
            try:
                writer.add_histogram(f'Gradients/{name}', grad, episode)
            except Exception as e:
                print(f"An error occurred during logging Gradients/{name}: {e}")

        # Log weights
        for name, weight in agent.logging_data['weights']:
            try:
                writer.add_histogram(f'Weights/{name}', weight, episode)
            except Exception as e:
                print(f"An error occurred during logging Weights/{name}: {e}")

        # Periodically update the target network
        if episode % 10 == 0:
            agent.update_target_network()



    # After all episodes, close the database and TensorBoard writer
    db.close()
    writer.close()

    # Optionally, save the agent's model
    torch.save(agent.policy_net.state_dict(), f"dqn_agent_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pth")

    # Plot the learning curve
    #plot_learning_curve(rewards)

if __name__ == "__main__":
    main_function()
