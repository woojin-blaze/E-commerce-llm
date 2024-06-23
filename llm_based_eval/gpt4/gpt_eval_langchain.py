import openai 
import json
import argparse
import tqdm
import time
import os
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import pandas as pd
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
    argparser.add_argument('--cleaning', action='store_true')
    args = argparser.parse_args()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    api_key = OPENAI_API_KEY


    with open(args.data_filepath, 'r', encoding='utf-8') as file:
        data_json = json.load(file)
    
    data = pd.DataFrame(data_json)
    with open(args.prompt_filepath, 'r', encoding='utf-8') as file: prompt = file.read()

    #prompt = open(args.prompt_filepath).read()
    
    llm = ChatOpenAI(model=args.model)
    prompt1 = ChatPromptTemplate.from_template(prompt) 
    cur_prompt = prompt
    parser = StrOutputParser()
    Raw_source = data["raw_source"]
    if args.data_type == 'pn':
        chain = {"Raw_source": RunnablePassthrough(), "Product_name": RunnablePassthrough()}| prompt1 | llm | parser
        Product_name = data["product_title"]
        product_info = list(zip(Raw_source, Product_name))
    elif args.data_type == 'cp':
        chain = {"Raw_source": RunnablePassthrough(), "Catch_phrase": RunnablePassthrough()}| prompt1 | llm | parser
        Catch_phrase = data["detailed_description"]
        product_info = list(zip(Raw_source, Catch_phrase))
    elif args.data_type == 'rk':
        chain = {"Raw_source": RunnablePassthrough(), "Recommended_keywords": RunnablePassthrough()}| prompt1 | llm | parser
        Recommended_keywords = data["related_search_keywords"]
        product_info = list(zip(Raw_source, Recommended_keywords))
    elif args.data_type == 'ct':
        #print("\nhere\n")
        chain = {"Raw_source": RunnablePassthrough(), "Product_category": RunnablePassthrough()}| prompt1 | llm | parser
        Product_category = data["product_category"]
        product_info = list(zip(Raw_source, Product_category))
        #print(product_info)
        #print(chain.invoke(product_info))
    elif args.data_type == 'sp':
        chain = {"Raw_source": RunnablePassthrough(), "Selling_point": RunnablePassthrough()}| prompt1 | llm | parser
        selling_point = data["product_selling_points"]
        product_info = list(zip(Raw_source, selling_point))
    
    scores = chain.batch(product_info, config={"max_concurrency": 15})
    #print(scores)
    scores_cleaned = []
    for score_str in scores:
        #print("\n",score_str)
        try:
            score = float(score_str.split(":")[-1].strip())
            scores_cleaned.append(score)
        except ValueError:
            scores_cleaned.append(None) 
    
    criteria = os.path.basename(args.prompt_filepath)  
    criteria_name = os.path.splitext(criteria)[0]  
    
    filtered_data_json = []
    for item, score in zip(data_json, scores_cleaned):
        if score is not None:
            item['score_' + args.data_type +"_"+ criteria_name] = score
            if (not args.cleaning) or (args.cleaning and score >= 4.0): 
                filtered_data_json.append(item)
            
    with open(args.save_filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered_data_json, f, ensure_ascii=False, indent=4)

