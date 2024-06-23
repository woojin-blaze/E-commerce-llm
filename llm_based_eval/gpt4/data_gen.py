import openai 
import json
import argparse
import tqdm
import time
import os
import dotenv
from dotenv import load_dotenv 

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
api_key = OPENAI_API_KEY
client = openai.OpenAI()

prompt = open('prompts/data_gen/gen_product_name_0.txt').read()
with open('data/raw_source.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

new_json = []
for instance in tqdm.tqdm(data):
    _response = client.chat.completions.create(
                        model='gpt-3.5-turbo-0125',
                        messages=[{"role": "system", "content": prompt}],
                        temperature=2,
                        max_tokens=5,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0,
                        stop=None,
                        # logprobs=40,
                        #n=20
                    )
    time.sleep(0.5)
    instance['response']= [_response.choices[i].message.content for i in range(len(_response.choices))]
    content=_response.choices[0].message.content
    print(content)
    new_json.append(instance)
    
with open('data/gen_raw_source.json', 'w', encoding='utf-8') as f:
        json.dump(new_json, f, ensure_ascii=False, indent=4)