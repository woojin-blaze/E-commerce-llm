import json
import os 

datafile_path = "data/data3_base_0501_last.json"

def cal_average(data_filepath):
    with open(data_filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)

    scores_sum = {}
    scores_count = {}

    for item in data:
        for key, value in item.items():
            if key.startswith('score_pn_') or key.startswith('score_cp_') or key.startswith('score_rk_'):
                scores_sum[key] = scores_sum.get(key, 0) + value
                scores_count[key] = scores_count.get(key, 0) + 1

    # Calculate individual averages
    averages = {key: scores_sum[key] / scores_count[key] for key in scores_sum}

    # Calculate category averages
    category_sums = {'pn': 0, 'cp': 0, 'rk': 0}
    category_counts = {'pn': 0, 'cp': 0, 'rk': 0}

    for score_type, avg in averages.items():
        if score_type.startswith('score_pn_'):
            category_sums['pn'] += avg
            category_counts['pn'] += 1
        elif score_type.startswith('score_cp_'):
            category_sums['cp'] += avg
            category_counts['cp'] += 1
        elif score_type.startswith('score_rk_'):
            category_sums['rk'] += avg
            category_counts['rk'] += 1

    category_averages = {cat: category_sums[cat] / category_counts[cat] for cat in category_sums}

    # Calculate total average across all categories
    total_average = sum(category_averages.values()) / len(category_averages)
    
    dataset = os.path.basename(data_filepath)  
    dataset_name = os.path.splitext(dataset)[0]  

    output_filepath = f"./results/average_score_{dataset_name}.json"
    results = {
        "individual_scores": averages,
        "category_averages": category_averages,
        "total_average": total_average
    }
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    print(f"Averages saved to {output_filepath}")
    
cal_average(datafile_path)