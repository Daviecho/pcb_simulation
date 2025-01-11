import torch
import torch.nn as nn
import torch.optim as optim
from gnn_model import GNNModel
from torch_geometric.data import Data
import torch_geometric
import random
import numpy as np
from collections import deque

class ReplayBuffer:
    def __init__(self, capacity=1000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        # Store transition as a tuple
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        # Sample a batch of transitions
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.array, zip(*batch))
        return state, action, reward, next_state, done

    def __len__(self):
        return len(self.buffer)

class DQNAgent:
    def __init__(self, node_feature_dim, hidden_dim, output_dim, writer=None, 
                 lr=1e-4, gamma=0.99, buffer_capacity=1000, batch_size=128, 
                 epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=15000):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy_net = GNNModel(node_feature_dim, hidden_dim, output_dim).to(self.device)
        self.target_net = GNNModel(node_feature_dim, hidden_dim, output_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.criteria = nn.MSELoss()

        self.replay_buffer = ReplayBuffer(capacity=buffer_capacity)
        self.batch_size = batch_size
        self.gamma = gamma

        self.steps_done = 0
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        self.writer = writer  # TensorBoard writer

        self.logging_data = {
            'action_rewards': {action: [] for action in range(output_dim)},
            'loss': [],
            'average_q': [],
            'gradients': [],
            'weights': [],
            'epsilon':[]
        }

    def accumulate_logging_data(self, action_batch, reward_batch, loss, state_action_values):
        """Accumulate data for logging."""
        # Accumulate action-reward data
        for action, reward in zip(action_batch, reward_batch):
            self.logging_data['action_rewards'][action].append(reward)
        
        # Accumulate loss and Q-values
        self.logging_data['loss'].append(loss.item())
        self.logging_data['average_q'].append(state_action_values.mean().item())

                
        # Accumulate gradients
        for name, param in self.policy_net.named_parameters():
            if param.grad is not None:
                self.logging_data['gradients'].append((name, param.grad.clone().cpu().numpy()))

        # Accumulate weights
        # for name, param in self.policy_net.named_parameters():
        #     self.logging_data['weights'].append((name, param.clone().cpu().numpy()))

    def select_action(self, state, available_actions):
        epsilon = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * \
                  np.exp(-1. * self.steps_done / self.epsilon_decay)
        self.steps_done += 1

        # Log epsilon
        self.logging_data['epsilon'].append(epsilon)

        if random.random() < epsilon:
            action = random.choice(available_actions)
        else:
            with torch.no_grad():
                data = self.prepare_data(state)
                q_values = self.policy_net(data)
                q_values = q_values.cpu().numpy()[0]
                available_q = q_values[available_actions]
                best_action_idx = np.argmax(available_q)
                action = available_actions[best_action_idx]
        
        return action

    def prepare_data(self, state):
        """
        Converts PCB state into torch_geometric Data object.
        Assumes state is a PCB instance.
        """
        nodes, edges = state.get_graph()
        x = torch.tensor(nodes, dtype=torch.float)
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        data = Data(x=x, edge_index=edge_index)        
        return data.to(self.device)

    def optimize_model(self):
        if len(self.replay_buffer) < self.batch_size:
            return

        state_batch, action_batch, reward_batch, next_state_batch, done_batch = self.replay_buffer.sample(self.batch_size)

        # Convert batches to tensors
        state_batch = [self.prepare_data(state) for state in state_batch]
        next_state_batch = [self.prepare_data(state) for state in next_state_batch]

        # Process all graphs in the batch
        state_batch = torch_geometric.data.Batch.from_data_list(state_batch).to(self.device)
        next_state_batch = torch_geometric.data.Batch.from_data_list(next_state_batch).to(self.device)

        # Compute current Q values
        q_values = self.policy_net(state_batch)
        state_action_values = q_values.gather(1, torch.tensor(action_batch, dtype=torch.long).unsqueeze(1).to(self.device))

        # Compute next Q values
        with torch.no_grad():
            next_q_values = self.target_net(next_state_batch).max(1)[0]
            expected_state_action_values = torch.tensor(reward_batch, dtype=torch.float).to(self.device) + \
                self.gamma * next_q_values * (1 - torch.tensor(done_batch, dtype=torch.float).to(self.device))

        # Compute loss
        loss = self.criteria(state_action_values.squeeze(), expected_state_action_values)

        # Accumulate logging data instead of writing immediately
        self.accumulate_logging_data(action_batch, reward_batch, loss, state_action_values)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())

        if self.writer:
            self.writer.add_scalar('Network/Target Network Updates', 1, self.steps_done)