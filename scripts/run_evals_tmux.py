#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import pynvml
import argparse
from pathlib import Path

def get_gpu_utilization():
    """Get GPU memory and utilization information for all GPUs"""
    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    
    gpu_info = []
    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        
        gpu_info.append({
            'gpu_id': i,
            'memory_used': info.used,
            'memory_total': info.total,
            'memory_percent': (info.used / info.total) * 100,
            'gpu_utilization': utilization.gpu,
            'memory_utilization': utilization.memory
        })
    
    pynvml.nvmlShutdown()
    return gpu_info

def find_least_used_gpu():
    """Find the least utilized GPU based on memory usage and GPU utilization"""
    gpu_info = get_gpu_utilization()
    
    # Calculate a combined score for each GPU
    for gpu in gpu_info:
        # Weight memory usage more heavily than GPU utilization
        gpu['score'] = (gpu['memory_percent'] * 0.7) + (gpu['gpu_utilization'] * 0.3)
    
    # Sort by score to find least used GPU
    gpu_info.sort(key=lambda x: x['score'])
    least_used = gpu_info[0]
    
    print(f"Selected GPU {least_used['gpu_id']} (Memory: {least_used['memory_percent']:.1f}%, GPU Util: {least_used['gpu_utilization']}%)")
    return least_used['gpu_id']

def read_commands(mode):
    """Read commands from the appropriate eval commands file based on mode"""
    commands_file = Path(__file__).parent.parent / "commands" / f"{mode}_eval_commands.txt"
    
    if not commands_file.exists():
        raise FileNotFoundError(f"Commands file not found: {commands_file}")
    
    commands = []
    with open(commands_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                commands.append(line)
    
    return commands

def check_tmux_session(session_name):
    """Check if tmux session exists"""
    try:
        result = subprocess.run(['tmux', 'has-session', '-t', session_name], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def create_tmux_session(session_name):
    """Create a new tmux session"""
    if check_tmux_session(session_name):
        print(f"Tmux session '{session_name}' already exists. Killing it...")
        subprocess.run(['tmux', 'kill-session', '-t', session_name])
        time.sleep(1)
    
    print(f"Creating tmux session: {session_name}")
    subprocess.run(['tmux', 'new-session', '-d', '-s', session_name])

def run_command_in_tmux_window(session_name, window_name, command, gpu_id):
    """Run a command in a new tmux window with proper environment setup"""
    
    # Create new window
    subprocess.run(['tmux', 'new-window', '-t', session_name, '-n', window_name])
    
    # Setup environment: source zshrc, activate conda env, cd to correct directory, set GPU
    setup_commands = [
        'source ~/.zshrc',
        'conda activate mirage_clenaed',
        'cd mirage/mirage/benchmark/robosuite',
        f'export CUDA_VISIBLE_DEVICES={gpu_id}',
        command
    ]
    
    # Send all commands to the window
    for cmd in setup_commands:
        subprocess.run(['tmux', 'send-keys', '-t', f'{session_name}:{window_name}', cmd, 'Enter'])
        time.sleep(0.5)  # Small delay between commands

def main():
    """Main function to orchestrate the tmux evaluation runs"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run evaluation commands in tmux with GPU management')
    parser.add_argument('mode', choices=['splotch', 'lighting', 'standard'], 
                       help='Evaluation mode: splotch, lighting, or standard')
    
    args = parser.parse_args()
    
    # Capitalize mode for display
    mode_display = args.mode.capitalize()
    
    print(f"Starting {mode_display} Evaluation Script with Tmux")
    print("=" * 50)
    
    try:

        # Read commands from file
        commands = read_commands(args.mode)
        print(f"Found {len(commands)} commands to run\n")
        
        # Create tmux session
        session_name = f"{args.mode}_evals"
        create_tmux_session(session_name)
        
        # Run each command in its own tmux window
        for i, command in enumerate(commands, 1):
            gpu_id = find_least_used_gpu()
            window_name = f"eval_{i}"
            print(f"Setting up window {i}/{len(commands)}: {window_name}")
            print(f"Command: {command[:80]}..." if len(command) > 80 else f"Command: {command}")
            
            run_command_in_tmux_window(session_name, window_name, command, gpu_id)
            time.sleep(20)  # Brief pause between window creation

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()