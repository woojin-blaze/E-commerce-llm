import json
import argparse


argparser = argparse.ArgumentParser()
argparser.add_argument('--filepath', type=str, default='results/catch_phrase/gpt4_rel_detailed_openai.json')
argparser.add_argument('--save_filepath', type=str, default='results/catch_phrase/cleaned_rel.json')
argparser.add_argument('--thre_score', type=float, default=3.5)
argparser.add_argument('--data_type', type=str, default='cp', help="Type of data to process: 'pn' for product name, 'cp' for catch phrase, or 'rk' for recommended keywords.")
#argparser.add_argument('--score_only', action='store_true')
args = argparser.parse_args()
    

with open(args.filepath, 'r', encoding='utf-8') as file:
    data = json.load(file)

def calculate_average(scores, threshold):
    # Attempt to convert scores to floats, ignoring invalid entries
    valid_scores = []
    invalid_count = 0
    
    for score in scores:
        try:
            valid_scores.append(float(score))
        except ValueError:
            invalid_count += 1
            
    # If more than two invalid entries, return average as 0
    if invalid_count > threshold:
        return 0
    else:
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0


filtered_data = []
for item in data:
    average_score = item["average_score_"+args.data_type]
    if average_score >= float(args.thre_score):
        item_filtered = {key: value for key, value in item.items() if key != "all_responses"}
        filtered_data.append(item_filtered)

with open(args.save_filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
