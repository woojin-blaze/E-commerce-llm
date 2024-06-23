import subprocess
import json
import argparse
import os



argparser = argparse.ArgumentParser()
argparser.add_argument('--data_filepath', type=str, default='./data/data_pair.json')
argparser.add_argument('--model', type=str, default='gpt-3.5-turbo-0125')
argparser.add_argument('--score_only', action='store_true', help='score_only 하면 클리닝 없이 점수만 매김')
args = argparser.parse_args()
data_pair_filepath = args.data_filepath


def run_evaluation(prompt_filepath, save_filepath, data_filepath, model, data_type):
    # Construct the command to run
    command = [
        'python3', 'gpt_eval_langchain.py',
        '--prompt_filepath', prompt_filepath,
        '--save_filepath', save_filepath,
        '--data_filepath', data_filepath,
        '--model', model,
        '--data_type', data_type
    ]
    
    # Run the command
    subprocess.run(command)

def run_cleaning(filepath, save_filepath, thre_score, data_type):
    # Construct the command to run
    command = [
        'python3', 'data_clean.py',
        '--filepath', filepath,
        '--save_filepath', save_filepath,
        '--thre_score', str(thre_score),
        '--data_type', data_type
    ]
    if args.score_only:
        command.append('--score_only')

    # Run the command
    subprocess.run(command)

def run_augment(prompt_filepath, save_filepath, data_filepath):
    # Construct the command to run
    command = [
        'python3', 'data_augment.py',
        '--prompt_filepath', prompt_filepath,
        '--save_filepath', save_filepath,
        '--data_filepath', data_filepath,
    ]
    
    # Run the command
    subprocess.run(command)
    
def run_integrate_cleaned(append_filepath, append, save_filepath, data_type):
    command = [
        'python3', 'integrate_cleaned.py',
        '--append_filepath', str(append_filepath),
        '--save_filepath', str(save_filepath),
        '--data_type', str(data_type)
    ]
    
    # For boolean flags, only add the flag to the command if it's True
    if append:
        command.append('--append')
        
    # Run the command
    subprocess.run(command)

def get_item_count(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return len(data)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0


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
        

# Criteria : 
# product name : coherance, relevance, searchable
# detailed description : harmlessness, relevance, sentencen completeness
# recommended keywords : daily used, 
configurations = {
    "product_name": {
        "evaluations": [
            {
                'prompt_filepath': './prompts/product_name/coher_detailed.txt',
                'save_filepath': './results/product_name/gpt4_coher_openai.json',
                'data_filepath': data_pair_filepath,
                'model': args.model,
                'data_type': 'pn'
            },
            {
                'prompt_filepath': './prompts/product_name/rel_detailed.txt',
                'save_filepath': './results/product_name/gpt4_rel_openai.json',
                'data_filepath': data_pair_filepath,
                'model': args.model,
                'data_type': 'pn'
            },
            {
                'prompt_filepath': './prompts/product_name/search_detailed.txt',
                'save_filepath': './results/product_name/gpt4_search_openai.json',
                'data_filepath': data_pair_filepath,
                'model': args.model,
                'data_type': 'pn'
            }
            # Add more evaluations if needed
        ],
        "cleanings": [
            {
                'filepath': './results/product_name/gpt4_coher_openai.json',
                'save_filepath': './results/product_name/cleaned_coher.json',
                'thre_score': 3,
                'data_type': 'pn'
            },
            {
                'filepath': './results/product_name/gpt4_rel_openai.json',
                'save_filepath': './results/product_name/cleaned_rel.json',
                'thre_score': 3,
                'data_type': 'pn'
            },
            {
                'filepath': './results/product_name/gpt4_search_openai.json',
                'save_filepath': './results/product_name/cleaned_search.json',
                'thre_score': 3,
                'data_type': 'pn'
            }
        ]
    },
    "catch_phrase": {
        "evaluations": [
            {
                'prompt_filepath': './prompts/promoeval/rel_detailed.txt',
                'save_filepath': './results/catch_phrase/gpt4_rel_openai.json',
                'data_filepath': "./results/product_name/integrate_cleaned_data.json",
                'model': args.model,
                'data_type': 'cp'
            },
            {
                'prompt_filepath': './prompts/promoeval/sen_comp_detailed.txt',
                'save_filepath': './results/catch_phrase/gpt4_sencomp_openai.json',
                'data_filepath': "./results/product_name/integrate_cleaned_data.json",
                'model': args.model,
                'data_type': 'cp'
            },
            {
                'prompt_filepath': './prompts/promoeval/harm_detailed.txt',
                'save_filepath': './results/catch_phrase/gpt4_harm_openai.json',
                'data_filepath': "./results/product_name/integrate_cleaned_data.json",
                'model': args.model,
                'data_type': 'cp'
            }
        ],
        "cleanings": [
            {
                'filepath': './results/catch_phrase/gpt4_rel_openai.json',
                'save_filepath': './results/catch_phrase/cleaned_rel.json',
                'thre_score': 3,
                'data_type': 'cp'
            },
            {
                'filepath': './results/catch_phrase/gpt4_sencomp_openai.json',
                'save_filepath': './results/catch_phrase/cleaned_sencomp.json',
                'thre_score': 3,
                'data_type': 'cp'
            },
            {
                'filepath': './results/catch_phrase/gpt4_harm_openai.json',
                'save_filepath': './results/catch_phrase/cleaned_harm.json',
                'thre_score': 3,
                'data_type': 'cp'
            }
        ]
    },
    "recommended_keywords": {
        "evaluations": [
            {
                'prompt_filepath': './prompts/recommendation/rel_detailed.txt',
                'save_filepath': './results/recommended_keywords/gpt4_rel_openai.json',
                'data_filepath': "./results/catch_phrase/integrate_cleaned_data.json",
                'model': args.model,
                'data_type': 'rk'
            },
            {
                'prompt_filepath': './prompts/recommendation/trend_detailed.txt',
                'save_filepath': './results/recommended_keywords/gpt4_trend_openai.json',
                'data_filepath': "./results/catch_phrase/integrate_cleaned_data.json",
                'model': args.model,
                'data_type': 'rk'
            },
            {
                'prompt_filepath': './prompts/recommendation/daily_detailed.txt',
                'save_filepath': './results/recommended_keywords/gpt4_daily_openai.json',
                'data_filepath': "./results/catch_phrase/integrate_cleaned_data.json",
                'model': args.model,
                'data_type': 'rk'
            }
            # Add more evaluations if needed
        ],
        "cleanings": [
            {
                'filepath': './results/recommended_keywords/gpt4_rel_openai.json',
                'save_filepath': './results/recommended_keywords/cleaned_rel.json',
                'thre_score': 3,
                'data_type': 'rk'
            },
            {
                'filepath': './results/recommended_keywords/gpt4_trend_openai.json',
                'save_filepath': './results/recommended_keywords/cleaned_trend.json',
                'thre_score': 3,
                'data_type': 'rk'
            },
            {
                'filepath': './results/recommended_keywords/gpt4_daily_openai.json',
                'save_filepath': './results/recommended_keywords/cleaned_daily.json',
                'thre_score': 3,
                'data_type': 'rk'
            }
        ]
    }
}

if args.score_only :
    for key in configurations:
        if 'evaluations' in configurations[key]:  
            for evaluation in configurations[key]['evaluations']:
                evaluation['save_filepath'] = data_pair_filepath  
                evaluation['data_filepath'] = data_pair_filepath

    for key in ['product_name', 'catch_phrase', 'recommended_keywords']:
        if key in configurations and 'evaluations' in configurations[key]:
            for eval_config in configurations[key]['evaluations']:
                run_evaluation(**eval_config)
                #print(eval_config)
    cal_average(data_pair_filepath)
    
else:
    for key in configurations:
        group = configurations[key]
        for eval_config in group['evaluations']:
            run_evaluation(**eval_config)

        for clean_config in group['cleanings']:
            run_cleaning(**clean_config)


        run_integrate_cleaned(data_pair_filepath, False, f"./results/{key}/integrate_cleaned_data.json", key)
    cal_average(data_pair_filepath)


