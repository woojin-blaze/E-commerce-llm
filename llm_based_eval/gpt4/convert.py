import pandas as pd

# Path to your CSV file
csv_file_path = '../../data/data3_base.csv'

# Path where you want to save the JSON file
json_file_path = 'data/data3_base_0501.json'

# Read the CSV file
df = pd.read_csv(csv_file_path)
df.rename(columns={'product_name_kor': 'raw_source'}, inplace=True)

df.reset_index(drop=True, inplace=True)

json_str = df.to_json(orient='records', force_ascii=False)


# Write the JSON string to a file, explicitly setting encoding to 'utf-8'
with open(json_file_path, 'w', encoding='utf-8') as file:
    file.write(json_str)

print(f'CSV file has been converted to JSON and saved to {json_file_path}')
