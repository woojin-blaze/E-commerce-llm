import argparse
import json
import os
import glob


# Setup the argument parser
argparser = argparse.ArgumentParser(description="Load a JSON file and save it to a new location.")
argparser.add_argument('--append_filepath', type=str, default='./data/data_pair.json')
argparser.add_argument('--append', action='store_true', help="append 하면 기존 데이터에 추가되는 형식")
argparser.add_argument('--save_filepath', type=str, default='./results/integrated_clean.json')
argparser.add_argument('--data_type', type=str, default='cp', help="Type of data to process: 'pn' for product name, 'cp' for catch phrase, or another value for recommended keywords.")

args = argparser.parse_args()

# Conditional logic based on the data_type argument
if args.data_type == 'pn':
    json_files = glob.glob('./results/product_name/cleaned*.json')
elif args.data_type == 'cp':
    json_files = glob.glob('./results/catch_phrase/cleaned*.json')
else:
    json_files = glob.glob('./results/recommended_keywords/cleaned*.json')

#json_files = ['./results/cleaned_rel.json', './results/cleaned_sencomp.json', './results/cleaned_harm.json'] 


all_data = []
for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        all_data.extend(data)
        
all_indexes = [item['index'] for item in all_data]
common_indexes = set(index for index in all_indexes if all_indexes.count(index) == len(json_files))

items_added = {}

# Filter all_data for items with 'index' in common_indexes, ensuring no duplicates
joined_data = []
for item in all_data:
    if item['index'] in common_indexes and item['index'] not in items_added:
        joined_data.append(item)
        items_added[item['index']] = True 

print("\njoining ", args.data_type, len(joined_data))

#save the integrate_cleaned
with open(args.save_filepath, 'w', encoding='utf-8') as f:
    json.dump(joined_data, f, ensure_ascii=False, indent=4)

if (args.append) :
    index =0
    try:
        with open(args.append_filepath, 'r+', encoding='utf-8') as file:
            # Load the existing data
            existing_data = json.load(file)
            # Determine the starting index for new data (if you want to continue the index sequentially)
            if existing_data:  # Check if the existing data is not empty
                index = existing_data[-1]['index'] + 1
                
            # Append the new data and reset indexes
            for item in joined_data:
                item['index'] = index
                existing_data.append(item)
                index += 1
                
            # Move back to the start of the file to overwrite it
            file.seek(0)
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
            # Truncate the file to the new size
            file.truncate()
        print("Data has been successfully appended and indexes reset.")
        
    except FileNotFoundError:
        print(f"Error: The file {args.append_filepath} was not found.")
else : 
    index = 0
    for item in joined_data:
        item['index'] = index
        index += 1

    try:
        with open(args.append_filepath, 'w', encoding='utf-8') as file:
            json.dump(joined_data, file, ensure_ascii=False, indent=4)
        print("Data has been successfully written to a new file.")
    except FileNotFoundError:
        print(f"Error: The file {args.append_filepath} could not be created.")


