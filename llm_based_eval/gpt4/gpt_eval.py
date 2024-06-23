import openai 
import json
import argparse
import tqdm
import time
import os
import dotenv
from dotenv import load_dotenv 

load_dotenv()

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
    
if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--prompt_filepath', type=str, default='prompts/promoeval/rel_detailed.txt')
    argparser.add_argument('--save_filepath', type=str, default='results/catch_phrase/gpt4_rel_detailed_openai.json')
    argparser.add_argument('--data_filepath', type=str, default='data/data_pair.json')
    argparser.add_argument('--data_type', type=str, default='cp', help="Type of data to process: 'pn' for product name, 'cp' for catch phrase, or 'rk' for recommended keywords.")
    argparser.add_argument('--model', type=str, default='gpt-3.5-turbo-0125')
    args = argparser.parse_args()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    api_key = OPENAI_API_KEY


    with open(args.data_filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    prompt = open(args.prompt_filepath).read()
    

    print(data[:1])

    ct, ignore = 0, 0
    client = openai.OpenAI()
    
    new_json = []
    
    for instance in tqdm.tqdm(data):

        source = instance.get('raw_source', '')
        cur_prompt = prompt
        if 'raw_source' in instance:
            cur_prompt = cur_prompt.replace('{{Raw_source}}', source)
        if 'product_title' in instance:
            system_output0 = instance['product_title']
            cur_prompt = cur_prompt.replace('{{Product_name}}', system_output0)
        if 'detailed_description' in instance:
            system_output1 = instance['detailed_description']
            cur_prompt = cur_prompt.replace('{{Catch_phrase}}', system_output1)
        if 'related_search_keywords' in instance:
            system_output2 = instance['related_search_keywords']
            cur_prompt = cur_prompt.replace('{{Recommended_keywords}}', system_output2)

        instance['prompt'] = cur_prompt

        while True:
            try:
                _response = client.chat.completions.create(
                    model=args.model,
                    messages=[{"role": "system", "content": cur_prompt}],
                    temperature=2,
                    max_tokens=5,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    # logprobs=40,
                    n=20
                )
                time.sleep(0.5)

                all_responses = [_response.choices[i].message.content for i in range(len(_response.choices))]
                average_score = calculate_average(all_responses,2)
                instance["average_score_"+args.data_type] = average_score
                new_json.append(instance)
                ct += 1
                break
            except Exception as e:
                print(e)
                if ("limit" in str(e)):
                    time.sleep(2)
                else:
                    ignore += 1
                    print('ignored', ignore)
                    print(f'Ignored instance due to error: {ignore}')
                    print(f'Error processing instance: {instance}')

                    break

    print('ignored total', ignore)

    
    with open(args.save_filepath, 'w', encoding='utf-8') as f:
        json.dump(new_json, f, ensure_ascii=False, indent=4)
