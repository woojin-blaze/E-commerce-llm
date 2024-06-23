import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
import os

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Split JSON data into training and testing datasets.')
    parser.add_argument('--data_filepath', type=str, default = './data/data_gen_0417.json')
    parser.add_argument('--test_size', type=float, default = 0.25)


    args = parser.parse_args()


    base_name = os.path.splitext(os.path.basename(args.data_filepath))[0]
    #base_name = "featureline"
    train_json_path = f'./data/{base_name}_train.json'
    test_json_path = f'./data/{base_name}_test.json'

    df = pd.read_json(args.data_filepath)

    test_size = args.test_size

    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)

    train_df.to_json(train_json_path, orient='records', force_ascii=False)
    test_df.to_json(test_json_path, orient='records', force_ascii=False)

    print(f"Data split into train ({train_json_path}) and test ({test_json_path}) datasets.")

if __name__ == '__main__':
    main()
