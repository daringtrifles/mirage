import json
import argparse
import os

def create_config(name, dataset):
    # Read the template file
    with open('robomimic-mirage/configs/template.json', 'r') as f:
        template = json.load(f)
    
    # Update the algo_name
    template['experiment']['name'] = name
    
    # Update the train/data/path in the template
    # train/data is a list containing dictionaries with path
    if 'train' in template and 'data' in template['train'] and isinstance(template['train']['data'], list):
        if len(template['train']['data']) > 0:
            template['train']['data'][0]['path'] = dataset
        else:
            # If the list is empty, add a new dictionary with the path
            template['train']['data'].append({'path': dataset})
    
    # Create the output filename
    output_file = f"robomimic-mirage/configs/{name}.json"
    
    # Write the new config file
    with open(output_file, 'w') as f:
        json.dump(template, f, indent=4)
    
    print(f"Created new config file: {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Create a new config file based on template.json')
    parser.add_argument('--name', type=str, required=True, help='Name of the new config file (without .json extension)')
    parser.add_argument('--dataset', type=str, required=True, help='Dataset path to use in the config')
    
    args = parser.parse_args()
    
    try:
        create_config(args.name, args.dataset)
    except Exception as e:
        print(f"Error creating config file: {str(e)}")

if __name__ == "__main__":
    main() 