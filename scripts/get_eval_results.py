from find_least_used_gpu import find_least_used_gpu

from pathlib import Path

# Create a new file
import numpy as np
import os
import sys
import csv
import json
import subprocess
import time
dp = True

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
    results = []
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
                    results.append({
                        'Exp Name': exp_name,
                        'Robot': map[robot.lower()],
                        'Num Rollouts': num_rollouts,
                        'Num Success': num_success,
                        'Success Rate': num_success/num_rollouts if num_rollouts > 0 else 0
                    })
    return results

def get_results_path(exp_name, robot):
    return f'mirage/mirage/benchmark/robosuite/results/{exp_name}/{robot}/target.txt'

if __name__ == "__main__":
    all_results = []
    exps = [

'panda_can',
'sawyer_can',
'jaco_can',
'ur5e_can',
'kinova3_can',
'panda_sawyer_can',
'panda_jaco_can',
'panda_ur5e_can',
'panda_kinova3_can',
'all_minus_jaco_merged_can',
'all_minus_kinova3_merged_can',
'all_minus_sawyer_merged_can',
'all_minus_ur5e_merged_can',
'all_can',
'panda_square',
'sawyer_square',
'jaco_square',
'ur5e_square',
'kinova3_square',
'panda_sawyer_square',
'panda_jaco_square',
'panda_ur5e_square',
'panda_kinova3_square',
'all_minus_jaco_merged_square',
'all_minus_kinova3_merged_square',
'all_minus_sawyer_merged_square',
'all_minus_ur5e_merged_square',
'all_square']
    for exp_name in exps:
        results = test_results(exp_name)
        all_results.extend(results)
    
    # Write results to CSV
    fieldnames = ['Exp Name', 'Robot', 'Num Rollouts', 'Num Success', 'Success Rate']
    with open('experiments_to_run_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    print('experiments_to_run_results.csv')
