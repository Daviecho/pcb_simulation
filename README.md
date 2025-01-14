Welcome to this repository, where we explore a **Reinforcement Learning (RL)** approach to optimize electronic waste (e-waste) management. By modeling Printed Circuit Board Assemblies (PCBAs) as graphs and leveraging **Graph Neural Networks (GNNs)**, this project efficiently determines the best inspection sequence (e.g. x-ray, visual inspection, flying probe) and, finally, the most profitable recovery strategies—reuse, repair, recycle, or remanufacture. Additionally, **Optuna** is used for hyperparameter optimization, and a **`.env`** file centralizes important configuration parameters.


In the rapidly growing domain of e-waste, **optimizing inspection and recovery strategies** for PCBAs is pivotal. This project uses:
- **Reinforcement Learning** for dynamic decision-making.
- **Graph Neural Networks** to handle variable PCB structures represented as graphs.
- **Optuna** for automated hyperparameter tuning.
- A **`.env`** file to manage crucial parameters (e.g., learning rate, buffer capacity) without hard-coding them.

With this setup, the system dynamically learns the best inspection steps and recovery methods to **maximize value** while **minimizing costs and environmental impact**.

- **Graph-Based Modeling**: Represents PCBAs as graphs so that each component (node) and connection (edge) is captured.
- **Reinforcement Learning Agent**: Uses RL to optimize sequential decisions (inspection → strategy).
- **Optuna Integration**: Automates hyperparameter optimization for efficient experiments.
- **`.env` Configuration**: Centralizes adjustable parameters (e.g., batch size, learning rate, gamma).
- **Economic & Environmental Focus**: Balances cost of inspections with potential profits from reuse, repair, or recycling.
- **Scalable & Extensible**: Facilitates adding new defect types, measurements, or strategies with minimal code changes.

---
## Installation - Prerequisites

- **Python 3**

- **PyTorch**, **Torch Geometric**, **SimPy**, **Optuna**, **Matplotlib**

## Run
1. **Clone the Repository**
    ```bash
    git clone https://github.com/Daviecho/pcb_simulation.git
    cd pcb_simulation
    ```

2. **Create & Activate a Virtual Environment (Optional)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3. **Configure** your `.env` file (e.g., episodes, num PCB per episode).

4. **Run** the main script:
    ```bash
    python main.py
    ```

5. **Monitor** training progress via console output or TensorBoard logs in `./tensorb`.
    ```bash
    tensorboard --logdir=tensorb
    ```

### Hyperparameter Optimization (Optuna)

1. **Set** initial guesses in `.env` (or let the script define search ranges).
2. **Run** optimization script:
    ```bash
    python opt.py
    ```
3. **Evaluate** the Optuna results, which update the RL agent’s configuration automatically or generate a best trial set of hyperparameters.

4. **TensorBoard** can be used to track the results:
    ```bash
    tensorboard --logdir=tensorb
    ```

5. Parameters are saved in folder opt and PCBA information is saved in an sqlite db in runs. In the folder runs the final trained agent is saved, too. 