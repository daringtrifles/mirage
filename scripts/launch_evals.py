from find_least_used_gpu import find_least_used_gpu


from pathlib import Path

# Create a new file

import os
import sys
import csv
import json
import subprocess
import time
import yaml
import os
import numpy as np
def generate_config(source_agent_path, target_agent_path, source_robot_name, target_robot_name, results_folder, output_path=None):
    """
    Generate a YAML configuration file based on the template with specified parameters.
    
    Args:
        source_agent_path (str): Path to the source agent model
        target_agent_path (str): Path to the target agent model
        source_robot_name (str): Name of the source robot
        target_robot_name (str): Name of the target robot
        results_folder (str): Path to store results
        output_path (str, optional): Path where the config file should be generated. 
                                   If None, will be generated in results_folder/config.yaml
    """
    # Template configuration
    config = {
        'source_agent_path': source_agent_path,
        'target_agent_path': target_agent_path,
        'naive': True,
        'n_rollouts': 50,
        'horizon': 350,
        'seed': 0,
        'passive': True,
        'connection': True,
        'source_robot_name': source_robot_name,
        'target_robot_name': target_robot_name,
        'source_tracking_error_threshold': 0.015,
        'source_num_iter_max': 300,
        'target_tracking_error_threshold': 0.015,
        'target_num_iter_max': 300,
        'delta_action': False,
        'enable_inpainting': False,
        'use_ros': False,
        'offline_eval': False,
        'use_diffusion': False,
        'diffusion_input_type': "",
        'results_folder': results_folder,
        'target_video_path': None,
        'source_video_path': None
    }
    
    # Create results folder if it doesn't exist
    os.makedirs(results_folder, exist_ok=True)
    
    # Determine output path
    if output_path is None:
        output_path = os.path.join(results_folder, 'config.yaml')
    else:
        # Create directory for output path if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write to YAML file
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Configuration file generated at: {output_path}")
    return output_path

def find_results(path):
    """Returns num_rollouts, num_success"""
    try:
        with open(path, 'r') as f:
            content = f.read().strip()
            # Split content into individual JSON objects
            json_objects = content.split('}{')
            if len(json_objects) > 1:
                # Add back the missing braces
                json_objects = [json_objects[0] + '}'] + ['{' + obj for obj in json_objects[1:]]
            
            # Parse the first JSON object which contains the main results
            data = json.loads(json_objects[0])
            num_rollouts = data.get('Num Rollouts', 0)
            num_success = data.get('Num_Success', [0])[0]
            return num_rollouts, num_success
    except FileNotFoundError:
        return 0, 0
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {path}")
        return 0, 0
    except Exception as e:
        print(f"Error reading results file: {str(e)}")
        return 0, 0

map = {'panda': 'Panda', 'sawyer': 'Sawyer', 'ur5e': 'UR5e', 'kinova3': 'Kinova3', 'jaco': 'Jaco', 'iiwa': 'IIWA'}
def test_results(exp_name):
    with open('experiments_to_run.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['exp_name'] == exp_name:

                # Get all non-None robots for this experiment
                robots = [robot for robot in [row['eval_robot_1'], row['eval_robot_2'], row['eval_robot_3'], row['eval_robot_4'], row['eval_robot_5']] 
                         if robot and robot.lower() != 'nan']

                for robot in robots:
                    results_path = get_results_path(exp_name, map[robot.lower()])
                    num_rollouts, num_success = find_results(results_path)
                    
                    

                    create_config(exp_name, map[robot.lower()])
                    time.sleep(5)  # Wait for 5 seconds
def get_results_path(exp_name, robot):
    return f'mirage/mirage/benchmark/robosuite/results/{exp_name}/{robot}/target.txt'

def get_absolute_path(relative_path):
    return str(os.path.abspath(relative_path))
def create_config(exp_name, robot):
    model_path = get_absolute_path(getModels(exp_name))
    results_folder = get_absolute_path(f'mirage/mirage/benchmark/robosuite/results/{exp_name}/{robot}')
    
    

    output_path = get_absolute_path(f'mirage/mirage/benchmark/robosuite/config/{exp_name}/{robot}.yaml')
    generate_config(
    source_agent_path=model_path,
    target_agent_path=model_path,
    source_robot_name="Panda",
    target_robot_name=robot,
    results_folder=results_folder,
    output_path=output_path
    )
    import os


    Path(results_folder + '/source.txt').touch()
    Path(results_folder + '/target.txt').touch()
    gpu_info = find_least_used_gpu()
    gpu_id = gpu_info['gpu_id']
    if gpu_info['gpu_utilization'] > 80 or gpu_info['memory_utilization'] > 95 or gpu_info['memory_percent'] > 80:
        print("GPU is too busy. Exiting...")
        print(f'didnt run {exp_name}_{robot}')
        sys.exit(1)

    command = f'source ~/.zshrc && conda activate mirage_clenaed && cd mirage/mirage/benchmark/robosuite && CUDA_VISIBLE_DEVICES={gpu_id} python run_robosuite_benchmark.py --config {output_path}'
    command += f' && read -p "Press Enter to close..."'
    run_in_tmux(command, f'{exp_name}_{robot}')


def getModels(folder_name):
    folder_path = f'robomimic-mirage/trained_diffusion_policies/{folder_name}'
    a=list_all_files(folder_path)
    for i in range(len(a)):
        if 'epoch_500' in a[i]:
            return a[i]
    

def list_subfolders(directory):
    """
    List all subfolders one level deep in the given directory.
    
    Args:
        directory (str): Path to the directory to search
    """
    try:
        # Get all entries in the directory
        entries = os.listdir(directory)
        
        # Filter for directories only
        subfolders = [entry for entry in entries 
                     if os.path.isdir(os.path.join(directory, entry))]
        
        # Print the subfolders
        return subfolders
            
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found")
    except PermissionError:
        print(f"Error: Permission denied to access '{directory}'")
    except Exception as e:
        print(f"Error: {str(e)}")


def list_all_files(directory):
    """
    List all files in a directory, including nested files.
    
    Args:
        directory (str): Path to the directory to search
    Returns:
        list: List of all file paths
    """
    file_list = []
    try:
        # Get all entries in the directory
        entries = sorted(os.listdir(directory))
        
        for entry in entries:
            full_path = os.path.join(directory, entry)
            
            if os.path.isdir(full_path):
                # If it's a directory, recursively get its contents
                file_list.extend(list_all_files(full_path))
            else:
                # If it's a file, add it to the list
                file_list.append(full_path)
                
    except FileNotFoundError: 
        print(f"Error: Directory '{directory}' not found")
    except PermissionError:
        print(f"Error: Permission denied to access '{directory}'")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return file_list

def run_in_tmux(command, window_name=None):
    """
    Run a command in a new tmux window.
    
    Args:
        command (str): The command to run
        window_name (str, optional): Name for the tmux window. If None, a default name will be used.
    """
    if window_name is None:
        window_name = f"window_{subprocess.getoutput('date +%s')}"
    
    try:
        # Create new window
        subprocess.run(['tmux', 'new-window', '-n', window_name], check=True)
        # Send the command to the window
        subprocess.run(['tmux', 'send-keys', '-t', window_name, command, 'C-m'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command in tmux: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    

    
    exps = ['panda_stack',
'sawyer_stack',
'jaco_stack',
'ur5e_stack',
'kinova3_stack',
'panda_sawyer_stack',
'panda_jaco_stack',
'panda_ur5e_stack',
'panda_kinova3_stack',
'all_minus_jaco_merged_stack',
'all_minus_kinova3_merged_stack',
'all_minus_sawyer_merged_stack',
'all_minus_ur5e_merged_stack',
'all_stack']
    for exp_name in list((exps)):
        test_results(exp_name)