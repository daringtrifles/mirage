#!/usr/bin/env python3
"""
Script to expand experiments_to_run.csv template for multiple tasks.
Takes a template CSV with {task} placeholders and generates expanded CSV for multiple tasks.
"""

import argparse
import pandas as pd
import os
from pathlib import Path


def expand_experiments_for_tasks(template_csv_path, tasks, output_csv_path):
    """
    Expand the template CSV for multiple tasks.
    
    Args:
        template_csv_path (str): Path to the template CSV file
        tasks (list): List of task names to expand for
        output_csv_path (str): Path where the expanded CSV will be saved
    """
    # Read the template CSV
    df_template = pd.read_csv(template_csv_path)
    
    # Remove any empty rows
    df_template = df_template.dropna(how='all')
    
    expanded_rows = []
    
    for task in tasks:
        print(f"Expanding template for task: {task}")
        
        # Create a copy of the template for this task
        df_task = df_template.copy()
        
        # Replace {task} placeholders in all columns
        for column in df_task.columns:
            if df_task[column].dtype == 'object':  # Only process string columns
                df_task[column] = df_task[column].astype(str).str.replace('{task}', task)
        
        # Add the rows for this task to our expanded list
        expanded_rows.append(df_task)
    
    # Combine all task-specific dataframes
    df_expanded = pd.concat(expanded_rows, ignore_index=True)
    
    # Save the expanded CSV
    df_expanded.to_csv(output_csv_path, index=False)
    print(f"Expanded CSV saved to: {output_csv_path}")
    print(f"Total rows in expanded CSV: {len(df_expanded)}")
    
    return df_expanded


def main():
    parser = argparse.ArgumentParser(description="Expand experiments CSV template for multiple tasks")
    
    parser.add_argument(
        "--template", 
        type=str, 
        default="experiments_to_run.csv",
        help="Path to template CSV file (default: experiments_to_run.csv)"
    )
    
    parser.add_argument(
        "--tasks", 
        type=str, 
        nargs='+',
        required=True,
        help="List of task names to expand for (e.g., --tasks lift stack pickup)"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        default="expanded_experiments_to_run.csv",
        help="Output CSV file path (default: expanded_experiments_to_run.csv)"
    )
    
    parser.add_argument(
        "--tasks-file",
        type=str,
        help="Optional: Read tasks from a file (one task per line)"
    )
    
    args = parser.parse_args()
    
    # Check if template file exists
    if not os.path.exists(args.template):
        print(f"Error: Template file '{args.template}' not found!")
        return 1
    
    # Get tasks from file if specified
    tasks = args.tasks
    if args.tasks_file:
        if os.path.exists(args.tasks_file):
            with open(args.tasks_file, 'r') as f:
                file_tasks = [line.strip() for line in f if line.strip()]
            tasks.extend(file_tasks)
            print(f"Added {len(file_tasks)} tasks from {args.tasks_file}")
        else:
            print(f"Warning: Tasks file '{args.tasks_file}' not found, using command line tasks only")
    
    # Remove duplicates while preserving order
    tasks = list(dict.fromkeys(tasks))
    
    print(f"Expanding template for {len(tasks)} tasks: {tasks}")
    
    # Expand the experiments
    try:
        expanded_df = expand_experiments_for_tasks(args.template, tasks, args.output)
        expanded_df.to_csv(args.output, index=False)
        
        # Show a preview of the results
        print("\nPreview of expanded experiments:")
        print(expanded_df.head(10).to_string())
        
        if len(expanded_df) > 10:
            print(f"... and {len(expanded_df) - 10} more rows")
            
        return 0
        
    except Exception as e:
        print(f"Error expanding experiments: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
#python3 scripts/expand_experiments_csv.py --template experiments_to_run_template.csv --tasks two_piece_assembly can lift stack square --output test_expanded_experiments.csv