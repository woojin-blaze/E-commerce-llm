import json
import argparse
import os



argparser = argparse.ArgumentParser()
argparser.add_argument('--data_filepath', type=str, default='./data/data_gen_0417.json')
args = argparser.parse_args()


score_thresholds = {
    "score_pn_coher_detailed": 3.5,
    "score_pn_rel_detailed": 4,
    "score_pn_search_detailed": 4,
    "score_cp_rel_detailed": 4,
    "score_cp_sen_comp_detailed": 4,
    "score_cp_harm_detailed": 4,
    "score_rk_rel_detailed": 4,
    "score_rk_trend_detailed": 3,
    "score_rk_daily_detailed": 4
}

def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: The file does not exist.")
        return None
    except json.JSONDecodeError:
        print("Error: File is not a valid JSON.")
        return None

def filter_data_by_thresholds(data, thresholds):
    filtered_data = []
    for item in data:
        include_item = True
        for score_type, threshold in thresholds.items():
            if item.get(score_type, 0) < threshold:
                include_item = False
                break
        if include_item:
            filtered_data.append(item)
    return filtered_data

def reset_index(filtered_data):
    for index, item in enumerate(filtered_data):
        item['index'] = index  # Resetting index
    return filtered_data

data = load_data(args.data_filepath)
if data is not None:
    filtered_results = filter_data_by_thresholds(data, score_thresholds)
    filtered_results = reset_index(filtered_results)
    
dataset = os.path.basename(args.data_filepath)  
dataset_name = os.path.splitext(dataset)[0]
output_filepath = f"./results/filtered_{dataset_name}.json"

with open(output_filepath, 'w', encoding='utf-8') as f:
    json.dump(filtered_results, f, ensure_ascii=False, indent=4)


