#!/usr/bin/env python3
"""
Script to categorize experiments in evaluation results CSV.
Adds a 'Category' column based on experiment naming patterns.
"""

import pandas as pd
import argparse
from pathlib import Path

def categorize_task_name(exp_name):
    if 'can' in exp_name:
        return "can"
    elif 'square' in exp_name:
        return "square"
    elif 'two_piece_assembly' in exp_name:
        return "two_piece_assembly"
    elif 'lift' in exp_name:
        return "lift"
    elif 'stack' in exp_name:
        return "stack"
    else:
        return "NA"
    
def categorize_experiment(exp_name, robot):
    """
    Categorize experiment based on experiment name and robot.
    
    Args:
        exp_name (str): Experiment name
        robot (str): Robot name
        
    Returns:
        str: Category ('NA', 'source', 'target', '1+1', 'n-1', 'n')
    """
    # If target robot is panda, category is "NA"
    if robot == "Panda":
        return "NA"
    

    if "all_minus" in exp_name:
        return "n-1"
    
    # If experiment name is "all", it's "n"
    elif exp_name.startswith("all_"):
        return "n"
    elif robot.lower() in exp_name and 'panda' in exp_name:
        return "1+1"
    
    elif 'panda' in exp_name:
        return "source"
    elif robot.lower() in exp_name:
        return "target"
    
    


def main():

    
    input_path = 'results/evaluation_results_standard_mode.csv'
    df = pd.read_csv(input_path)
    
    # Add category column
    print("Adding category column...")
    df['Category'] = df.apply(lambda row: categorize_experiment(row['Exp Name'], row['Robot']), axis=1)
    df['Task'] = df.apply(lambda row: categorize_task_name(row['Exp Name']), axis=1)


    
    # Show sample of categorized data
    print("\nSample of categorized data:")
    df.sort_values(by=['Robot', 'Task'], inplace=True)
    df.to_csv('results/evaluation_results_standard_mode_categorized.csv', index=False)
    
    import matplotlib.pyplot as plt
    import numpy as np

    # Define the order of categories for consistent plotting
    category_order = ['source', 'target', '1+1', 'n', 'n-1']
    robot_order = ['Panda', 'UR5e', 'Kinova3', 'Sawyer', 'Jaco']

    # Calculate average success rates for each robot-category combination
    robot_category_avg = {}
    
    for robot in robot_order:
        robot_df = df[df['Robot'] == robot]
        robot_category_avg[robot] = {}
        
        for cat in category_order:
            cat_data = robot_df[robot_df['Category'] == cat]['Success Rate']
            if not cat_data.empty:
                robot_category_avg[robot][cat] = cat_data.mean()
            else:
                robot_category_avg[robot][cat] = 0

    # Create the combined plot
    fig, ax = plt.subplots(figsize=(12, 8))
    bar_width = 0.15
    x = np.arange(len(robot_order))

    # Plot bars for each category
    for i, cat in enumerate(category_order):
        success_rates = [robot_category_avg[robot][cat] for robot in robot_order]
        x_pos = x + i * bar_width
        ax.bar(x_pos, success_rates, bar_width, label=cat, alpha=0.8)
        
        # Add value labels on top of bars
        for j, (x_pos_j, rate) in enumerate(zip(x_pos, success_rates)):
            if rate > 0:
                ax.text(x_pos_j, rate + 0.01, f'{rate:.2f}', 
                       ha='center', va='bottom', fontsize=8, rotation=90)

    # Customize the plot
    ax.set_xlabel('Robot')
    ax.set_ylabel('Average Success Rate')
    ax.set_title('Average Success Rate by Robot Across All Tasks')
    ax.set_xticks(x + bar_width * 2)  # Center the x-ticks
    ax.set_xticklabels(robot_order)
    ax.set_ylim(0, 1.1)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/all_robots_category_average_success_rate.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Print summary statistics
    print("\nAverage Success Rates by Robot and Category:")
    print("=" * 50)
    for robot in robot_order:
        print(f"\n{robot}:")
        for cat in category_order:
            avg_rate = robot_category_avg[robot][cat]
            print(f"  {cat}: {avg_rate:.3f}")


if __name__ == "__main__":
    exit(main())