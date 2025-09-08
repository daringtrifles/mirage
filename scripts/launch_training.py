import subprocess
import sys
import os
import time

from create_config import create_config
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

def main():

    if len(sys.argv) != 3:
        print("Usage: python launch_dp_experiment.py <name> <dataset>")
        sys.exit(1)
    
    exp_name = sys.argv[1]
    dataset = sys.argv[2]
    
    try:
        # Create the config file
        print("Creating config file...")
        config_path = create_config(exp_name, dataset)
        
        # Find the least used GPU
        print("Finding least used GPU...")
        
        gpu_info = find_least_used_gpu()
        
        # Create tmux window and run the experiment
        print(f"Creating tmux window and launching experiment on GPU {gpu_info['gpu_id']}...")
        print(f"GPU Utilization: {gpu_info['gpu_utilization']}%")
        print(f"Memory Usage: {gpu_info['memory_percent']:.1f}%")
        
        if gpu_info['gpu_utilization'] > 80 or gpu_info['memory_utilization'] > 80 or gpu_info['memory_percent'] > 80:
            print("GPU is too busy. Exiting...")
            sys.exit(1)
        
        create_tmux_window(gpu_info['gpu_id'], exp_name)
        
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
    time.sleep(20)