# example_optuna.py
import optuna
import os
from main import main_function
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables

load_dotenv()

OPT_STEPS = int(os.getenv("OPT_STEPS", 4))

def objective(trial):
    # Suggest piecewise parameters for test bonus as an example
    tb_start = trial.suggest_float("test_bonus_start", -10, 30)
    tb_zero = trial.suggest_float("test_bonus_zero_progress", 0.01, 0.9)
    tb_end = trial.suggest_float("test_bonus_end", -10, 30)
    tb_end_prog = trial.suggest_float("test_bonus_end_progress", tb_zero + 0.01, 1.0)

    # Set environment variables before main_function
    os.environ["TEST_BONUS_START"] = str(tb_start)
    os.environ["TEST_BONUS_ZERO_PROGRESS"] = str(tb_zero)
    os.environ["TEST_BONUS_END"] = str(tb_end)
    os.environ["TEST_BONUS_END_PROGRESS"] = str(tb_end_prog)

    # Repeat for recycle, repair, reuse if you want those optimized as well

    # Run the training. Make sure main_function() returns a numeric metric.
    average_reward = main_function()
    return average_reward

if __name__ == "__main__":
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=OPT_STEPS)

    print("Best parameters:", study.best_params)
    print("Best value:", study.best_value)
