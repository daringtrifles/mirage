import csv
import pandas as pd
csv_path = "experiments_to_run.csv"
df = pd.read_csv(csv_path)

for index, row in df.iterrows():
    exp_name = row['exp_name']
    train_data_filepath = row['train_data_filepath']
    print(f'python scripts/launch_training.py {exp_name} ../../../{train_data_filepath}')