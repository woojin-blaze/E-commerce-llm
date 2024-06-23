import argparse
import json
import os
import pandas as pd

data_filepath1 = "./results/category/ct_filtered_0417.json"
data_filepath2 = "./results/selling_point/sp_filtered_0417.json"
with open(data_filepath1, 'r', encoding='utf-8') as file:
    data1 = json.load(file)
    
with open(data_filepath2, 'r', encoding='utf-8') as file:
    data2 = json.load(file)

filtered_data1 = [item for item in data1 if item["score_ct_corr_detailed"] >= 4.0]

lookup = {item['raw_source']: item for item in filtered_data1}

joined_data = [item2 for item2 in data2 if item2['raw_source'] in lookup]
for item in joined_data:
    item['score_ct_corr_detailed'] = lookup[item['raw_source']]['score_ct_corr_detailed']

#df = pd.DataFrame(data2)

# Reset the index, and drop the old index
#df.reset_index(drop=True, inplace=True)

output_filepath = "./results/updated_filtered_0417.json"
#df.to_json(output_filepath, orient='records', indent=4, ensure_ascii=False)


with open(output_filepath, 'w', encoding='utf-8') as file:
    json.dump(data2, file, indent=4, ensure_ascii=False)