import argparse
import json
import os
import openai
import tqdm
import time
from dotenv import load_dotenv 

load_dotenv()

# Setup argument parser
argparser = argparse.ArgumentParser()
argparser.add_argument('--prompt_filepath', type=str, default='prompts/augment/pure_augment.txt')
argparser.add_argument('--save_filepath', type=str, default='results/augmented_data.json')
argparser.add_argument('--data_filepath', type=str, default='data/data_pair.json')
argparser.add_argument('--model', type=str, default='gpt-4-turbo-preview')
args = argparser.parse_args()

# Load OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

openai.api_key = OPENAI_API_KEY

# Load data from the specified JSON file
with open(args.data_filepath, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Load the prompt
prompt = open(args.prompt_filepath, 'r').read()

# Initialize counters
ct, ignore = 0, 0
client = openai.OpenAI()
cnt = 0
exit_flag = False

new_json = []

for instance in tqdm.tqdm(data):
    
    if exit_flag:
        break
    source = instance['original_kor']
    system_output = instance['advertising_kor']
    cur_prompt = prompt.replace('{{Product_name}}', source).replace('{{Catch_phrase}}', system_output)
    instance['prompt'] = cur_prompt

    while True:
        try:
            _response = client.chat.completions.create(
                model=args.model,
                messages=[{"role": "system", "content": cur_prompt}],
                temperature=0.7,
                max_tokens=70,
                #top_p=1,
                #frequency_penalty=0,
                #presence_penalty=0,
                stop=None,
                n=2
            )
            time.sleep(0.5) 
            generated_data = [_response.choices[i].message.content for i in range(len(_response.choices))]
            #print("\n", generated_data)
            instance['generated_data'] = generated_data
            new_json.append(instance)
            ct += 1
            
            
            #in case you want to end up early
            #cnt += 1
            #if cnt >= 20:
            #    exit_flag = True
            #    break
            
            break
        except Exception as e:
            print(e)
            if "limit" in str(e).lower():
                print("Rate limit error, waiting 2 seconds...")
                time.sleep(2)
            else:
                ignore += 1
                print('Ignored', ignore)
                print(f'Ignored instance due to error: {instance}')
                break
        



# new_json = 기존 데이터 + 새로 만든 데이터
transformed_items = []
index = 0  # Initialize index to keep track of the new index for each item

for item in new_json:
    # Process generated_data to create new items
    if 'generated_data' in item:
        for gen in item['generated_data']:
            # Splitting the generated string into the product name and catch phrase
            parts = gen.split('\n\n')
            if len(parts) >= 2:  # Ensure there are at least two parts
                new_product_name = parts[0].replace('New Product Name: ', '').strip()
                promotional_catch_phrase = parts[1].replace('Promotional Catch Phrase: ', '').strip()

                # Create a new item dictionary for each generated data entry
                new_item = {
                    'index': index,
                    'original_kor': new_product_name,
                    'advertising_kor': promotional_catch_phrase
                }
                transformed_items.append(new_item)
                index += 1  # Increment index for each new item

    # Remove 'generated_data' from the original item and update its index
    #item_modified = {key: value for key, value in item.items() if key != "generated_data"}
    #item_modified['index'] = index  # Update the index for the modified original item
    #transformed_items.append(item_modified)
    #index += 1  # Increment index for the modified original item


with open(args.save_filepath, 'w', encoding='utf-8') as f:
    json.dump(transformed_items, f, ensure_ascii=False, indent=4)

