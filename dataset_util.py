import pandas as pd
from datasets import load_dataset
def load_data(repo="bittensor-dataset/twitter-text-dataset"):
    dataset = load_dataset(repo)
    return dataset
def get_num_rows(dataset):
    num_rows = dataset['train'].num_rows
    return num_rows
if __name__=="__main__":
    dataset = load_data()
    num_rows = dataset['train'].num_rows
    load_data()
    