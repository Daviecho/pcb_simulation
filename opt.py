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
    tb_start = trial.suggest_float("test_bonus_start", 0, 30)
    tb_zero = trial.suggest_float("test_bonus_zero_progress", 0.01, 0.9)
    tb_end = trial.suggest_float("test_bonus_end", -10, 0)
    tb_end_prog = trial.suggest_float("test_bonus_end_progress", tb_zero + 0.01, 1.0)

    # Set environment variables before main_function
    os.environ["TEST_BONUS_START"] = str(tb_start)
    os.environ["TEST_BONUS_ZERO_PROGRESS"] = str(tb_zero)
    os.environ["TEST_BONUS_END"] = str(tb_end)
    os.environ["TEST_BONUS_END_PROGRESS"] = str(tb_end_prog)

    hidden_dim = trial.suggest_int("hidden_dim", 8, 128)
    os.environ["HIDDEN_DIM"] = str(hidden_dim)
    # Repeat for recycle, repair, reuse if you want those optimized as well


    # Prepare hyperparameters as a dictionary
    parameters = {
        "test_bonus_start": tb_start,
        "test_bonus_zero_progress": tb_zero,
        "test_bonus_end": tb_end,
        "test_bonus_end_progress": tb_end_prog,
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
