import subprocess
import sys
import os
import time
import pandas as pd
from find_least_used_gpu import find_least_used_gpu

def create_tmux_window(gpu_id, config_name):
    # Create a new tmux window with a specific name
    window_name = f"{config_name}"
    
    # Create the tmux window
    subprocess.run(['tmux', 'new-window', '-n', window_name])
    
    # Send the command to the new window
    config_path = f"robomimic-mirage/configs/{config_name}.json"
    command = "source ~/.zshrc && conda activate mirage_oxe_aug && cd robomimic-mirage/robomimic/scripts"
    command += f" && CUDA_VISIBLE_DEVICES={gpu_id} python train.py --config ../../../{config_path}; read -p 'Press Enter to close...'"
    subprocess.run(['tmux', 'send-keys', '-t', window_name, command, 'C-m'])
    
    # List all tmux windows
    print("\nCurrent tmux windows:")
    subprocess.run(['tmux', 'list-windows'])
def launch_training(exp_name):

    gpu_info = find_least_used_gpu()
    if  gpu_info['memory_utilization'] > 90 or gpu_info['memory_percent'] > 90:
        print("GPU is too busy. Exiting...")
        sys.exit(1)
    csv_path = "experiments_to_run.csv"
    df = pd.read_csv(csv_path)

    for index, row in df.iterrows():
        exp_name = row['exp_name']
        train_data_filepath = row['train_data_filepath']
        print(f'python scripts/launch_training.py {exp_name} ../../../{train_data_filepath}')
        
    create_tmux_window(gpu_info['gpu_id'], exp_name)
        
        

if __name__ == "__main__":
    experiments_to_run = pd.read_csv('experiments_to_run.csv')
    for _, row in experiments_to_run.iterrows():
        launch_training(row['exp_name'])
        time.sleep(20)