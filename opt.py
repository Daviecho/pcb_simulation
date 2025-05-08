#!/usr/bin/env python3

from datetime import datetime
import optuna
import os
from main import main_function
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables
from db_manager import DatabaseManager
import json 

load_dotenv()

OPT_STEPS = int(os.getenv("OPT_STEPS", 4))

def objective(trial):
    # Suggest piecewise parameters for test bonus as an example
    # Agent Hyperparameters
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    gamma = trial.suggest_float("gamma", 0.9, 0.999)
    epsilon_decay = trial.suggest_int("epsilon_decay", 5000, 50000) # Adjust range based on total steps
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128, 256])
    buffer_capacity = trial.suggest_int("buffer_capacity", 10000, 100000)
    hidden_dim_agent = trial.suggest_categorical("hidden_dim_agent", [32, 64, 128, 256]) # For the agent's GNN or FC layers

    # Suggest piecewise parameters for X-Ray Bonus
    xray_bonus_zero_progress = trial.suggest_float("xray_bonus_zero_progress", 0.01, 0.9)
    xray_bonus_end_progress = trial.suggest_float("xray_bonus_end_progress", xray_bonus_zero_progress + 0.01, 1.0)
    xray_bonus_start = trial.suggest_float("xray_bonus_start", -20, 50)
    xray_bonus_end = trial.suggest_float("xray_bonus_end", -30, 30)

    # Suggest piecewise parameters for Visual Inspection Bonus
    visual_bonus_zero_progress = trial.suggest_float("visual_bonus_zero_progress", 0.01, 0.9)
    visual_bonus_end_progress = trial.suggest_float("visual_bonus_end_progress", visual_bonus_zero_progress + 0.01, 1.0)
    visual_bonus_start = trial.suggest_float("visual_bonus_start", -20, 40)
    visual_bonus_end = trial.suggest_float("visual_bonus_end", -30, 20)

    # Suggest piecewise parameters for Flying Probe Bonus
    flying_probe_bonus_zero_progress = trial.suggest_float("flying_probe_bonus_zero_progress", 0.01, 0.9)
    flying_probe_bonus_end_progress = trial.suggest_float("flying_probe_bonus_end_progress", flying_probe_bonus_zero_progress + 0.01, 1.0)
    flying_probe_bonus_start = trial.suggest_float("flying_probe_bonus_start", -20, 50)
    flying_probe_bonus_end = trial.suggest_float("flying_probe_bonus_end", -30, 30)
    
    # Suggest piecewise parameters for Recycle Bonus
    recycle_bonus_zero_progress = trial.suggest_float("recycle_bonus_zero_progress", 0.01, 0.9)
    recycle_bonus_end_progress = trial.suggest_float("recycle_bonus_end_progress", recycle_bonus_zero_progress + 0.01, 1.0)
    recycle_bonus_start = trial.suggest_float("recycle_bonus_start", -20, 30)
    recycle_bonus_end = trial.suggest_float("recycle_bonus_end", -30, 40)

    # Suggest piecewise parameters for Repair Bonus
    repair_bonus_zero_progress = trial.suggest_float("repair_bonus_zero_progress", 0.01, 0.9)
    repair_bonus_end_progress = trial.suggest_float("repair_bonus_end_progress", repair_bonus_zero_progress + 0.01, 1.0)
    repair_bonus_start = trial.suggest_float("repair_bonus_start", -20, 30)
    repair_bonus_end = trial.suggest_float("repair_bonus_end", -30, 40)

    # Suggest piecewise parameters for Reuse Bonus
    reuse_bonus_zero_progress = trial.suggest_float("reuse_bonus_zero_progress", 0.01, 0.9)
    reuse_bonus_end_progress = trial.suggest_float("reuse_bonus_end_progress", reuse_bonus_zero_progress + 0.01, 1.0)
    reuse_bonus_start = trial.suggest_float("reuse_bonus_start", -20, 50)
    reuse_bonus_end = trial.suggest_float("reuse_bonus_end", -30, 50)

    # GNN Model hidden dimension (if different from agent's general hidden_dim or if you have a separate GNN model)
    # The existing code had "HIDDEN_DIM". If this is for the GNN specifically:
    gnn_hidden_dim = trial.suggest_int("gnn_hidden_dim", 8, 128) 


    # Set environment variables for the main_function call
    os.environ["AGENT_LR"] = str(lr)
    os.environ["AGENT_GAMMA"] = str(gamma)
    os.environ["AGENT_EPSILON_DECAY"] = str(epsilon_decay)
    os.environ["AGENT_BATCH_SIZE"] = str(batch_size)
    os.environ["AGENT_BUFFER_CAPACITY"] = str(buffer_capacity)
    os.environ["AGENT_HIDDEN_DIM"] = str(hidden_dim_agent) # Assuming agent uses this

    os.environ["XRAY_BONUS_ZERO_PROGRESS"] = str(xray_bonus_zero_progress)
    os.environ["XRAY_BONUS_END_PROGRESS"] = str(xray_bonus_end_progress)
    os.environ["XRAY_BONUS_START"] = str(xray_bonus_start)
    os.environ["XRAY_BONUS_END"] = str(xray_bonus_end)
    
    os.environ["VISUAL_BONUS_ZERO_PROGRESS"] = str(visual_bonus_zero_progress)
    os.environ["VISUAL_BONUS_END_PROGRESS"] = str(visual_bonus_end_progress)
    os.environ["VISUAL_BONUS_START"] = str(visual_bonus_start)
    os.environ["VISUAL_BONUS_END"] = str(visual_bonus_end)

    os.environ["FLYING_PROBE_BONUS_ZERO_PROGRESS"] = str(flying_probe_bonus_zero_progress)
    os.environ["FLYING_PROBE_BONUS_END_PROGRESS"] = str(flying_probe_bonus_end_progress)
    os.environ["FLYING_PROBE_BONUS_START"] = str(flying_probe_bonus_start)
    os.environ["FLYING_PROBE_BONUS_END"] = str(flying_probe_bonus_end)

    os.environ["RECYCLE_BONUS_ZERO_PROGRESS"] = str(recycle_bonus_zero_progress)
    os.environ["RECYCLE_BONUS_END_PROGRESS"] = str(recycle_bonus_end_progress)
    os.environ["RECYCLE_BONUS_START"] = str(recycle_bonus_start)
    os.environ["RECYCLE_BONUS_END"] = str(recycle_bonus_end)

    os.environ["REPAIR_BONUS_ZERO_PROGRESS"] = str(repair_bonus_zero_progress)
    os.environ["REPAIR_BONUS_END_PROGRESS"] = str(repair_bonus_end_progress)
    os.environ["REPAIR_BONUS_START"] = str(repair_bonus_start)
    os.environ["REPAIR_BONUS_END"] = str(repair_bonus_end)

    os.environ["REUSE_BONUS_ZERO_PROGRESS"] = str(reuse_bonus_zero_progress)
    os.environ["REUSE_BONUS_END_PROGRESS"] = str(reuse_bonus_end_progress)
    os.environ["REUSE_BONUS_START"] = str(reuse_bonus_start)
    os.environ["REUSE_BONUS_END"] = str(reuse_bonus_end)
    
    os.environ["GNN_HIDDEN_DIM"] = str(gnn_hidden_dim) # If GNN model uses this

    # Prepare hyperparameters as a dictionary for saving
    parameters = {
        "lr": lr,
        "gamma": gamma,
        "epsilon_decay": epsilon_decay,
        "batch_size": batch_size,
        "buffer_capacity": buffer_capacity,
        "hidden_dim_agent": hidden_dim_agent,
        "gnn_hidden_dim": gnn_hidden_dim,

        "xray_bonus_zero_progress": xray_bonus_zero_progress,
        "xray_bonus_end_progress": xray_bonus_end_progress,
        "xray_bonus_start": xray_bonus_start,
        "xray_bonus_end": xray_bonus_end,

        "visual_bonus_zero_progress": visual_bonus_zero_progress,
        "visual_bonus_end_progress": visual_bonus_end_progress,
        "visual_bonus_start": visual_bonus_start,
        "visual_bonus_end": visual_bonus_end,

        "flying_probe_bonus_zero_progress": flying_probe_bonus_zero_progress,
        "flying_probe_bonus_end_progress": flying_probe_bonus_end_progress,
        "flying_probe_bonus_start": flying_probe_bonus_start,
        "flying_probe_bonus_end": flying_probe_bonus_end,

        "recycle_bonus_zero_progress": recycle_bonus_zero_progress,
        "recycle_bonus_end_progress": recycle_bonus_end_progress,
        "recycle_bonus_start": recycle_bonus_start,
        "recycle_bonus_end": recycle_bonus_end,

        "repair_bonus_zero_progress": repair_bonus_zero_progress,
        "repair_bonus_end_progress": repair_bonus_end_progress,
        "repair_bonus_start": repair_bonus_start,
        "repair_bonus_end": repair_bonus_end,

        "reuse_bonus_zero_progress": reuse_bonus_zero_progress,
        "reuse_bonus_end_progress": reuse_bonus_end_progress,
        "reuse_bonus_start": reuse_bonus_start,
        "reuse_bonus_end": reuse_bonus_end,
    }
    
    # Run the training. Make sure main_function() returns a numeric metric.
    average_reward = main_function()
    # Save the parameters and objective value to a JSON file
    save_hyperparameters_as_json(parameters, average_reward, trial.number)

    return average_reward

opt_dir=""
def save_hyperparameters_as_json(parameters, objective_value, fileid):
    """
    Save hyperparameters and their objective value to a timestamped JSON file in the 'opt' folder.

    Args:
        parameters (dict): Hyperparameters to save.
        objective_value (float): The resulting objective value.
    """
    filename = os.path.join(opt_dir, f"opt_{fileid}.json")

    # Prepare the data
    data = {
        "parameters": parameters,
        "objective_value": objective_value,
        "timestamp": timestamp,
    }

    # Save to a JSON file
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved hyperparameters to {filename}")


if __name__ == "__main__":
    # Generate a timestamped filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Create the 'opt' folder if it doesn't exist
    opt_dir = os.path.join('opt', timestamp)
    os.makedirs(opt_dir, exist_ok=True)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=OPT_STEPS)

    print("Best parameters:", study.best_params)
    print("Best value:", study.best_value)
    # Save the best configuration using the existing function
    best_trial_number = study.best_trial.number
    save_hyperparameters_as_json(study.best_params, study.best_value, fileid=f"best_config_trial_{best_trial_number}")
