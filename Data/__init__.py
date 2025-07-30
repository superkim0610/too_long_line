import os
import pandas as pd
from math import ceil
import time
from tqdm import tqdm

import Data.address_processing as ap
import Data.type_processing as tp

def raw_csvs_to_integrated_raw_csv():
    raw_path = "Database/raw"
    raw_df_list = []

    for file_name in os.listdir(raw_path):
        if file_name.endswith("_raw.csv"):
            _df = pd.read_csv(os.path.join(raw_path, file_name))
            raw_df_list.append(_df)

    integrated_raw_path = "Database/integrated_raw"
    if not os.path.exists(integrated_raw_path):
        os.makedirs(integrated_raw_path)

    df = pd.concat(raw_df_list, ignore_index=True)

    # drop duplicates
    df.drop_duplicates(subset=["restaurant_name"], keep="first", inplace=True)
    df.to_csv(f"{integrated_raw_path}/integrated_raw.csv", index=False)

def add_lat_lon_to_integrated_raw_csv():
    ap.add_lat_lon_to_integrated_raw_csv("Database/integrated_raw/integrated_raw.csv", "Database/restaurant_address/restaurant_address.csv")

def classify_restaurant_type_to_integrated_raw_csv():
    org_df = pd.read_csv("Database/integrated_raw/integrated_raw.csv")

    rc = org_df["restaurant_category"]
    rc = list(set(rc))
    print("length of rc :", len(rc))

    rc_batches = []
    for i in range(ceil(len(rc)/10)):
        rc_batches.append(rc[i*10:min((i+1)*10, len(rc))])

    mapping_dict = dict()
    for rc_batch in tqdm(rc_batches):
        mapping_dict = mapping_dict | tp.restaurant_category_to_restaurant_type(rc_batch)


    org_df["restaurant_type"] = org_df["restaurant_category"].map(mapping_dict)
    org_df.to_csv("Database/restaurant_type/restaurant_type.csv", index=False)

def calc_review_ratio_to_integrated_raw_csv():
    df = pd.read_csv("Database/integrated_raw/integrated_raw.csv")
    df["review_num"] = df["review_num"].apply(eval)
    df = df[df["review_num"].apply(lambda x: x.get("total_num") is not None)]


    def calculate_ratio(d):
        total = d["total_num"]
        return {
            k.replace("_num", "_ratio"): v / total
            for k, v in d.items()
            if k != "total_num"
        }

    df["review_ratio"] = df["review_num"].apply(calculate_ratio)

    def remove_total_num(d):
        if "total_num" in d:
            del d["total_num"]
        return d

    df["review_ratio"] = df["review_ratio"].apply(remove_total_num)
    df.to_csv("Database/review_ratio/review_ratio.csv", index=False)

def integrated_raw_csv_to_data_csv():
    df_addr = pd.read_csv("Database/restaurant_address/restaurant_address.csv")

    df_type = pd.read_csv("Database/restaurant_type/restaurant_type.csv")
    df_type.drop(columns=["restaurant_category","restaurant_address","restaurant_tel","review_num"], inplace=True)

    df_ratio = pd.read_csv("Database/review_ratio/review_ratio.csv")
    df_ratio.drop(columns=["restaurant_category", "restaurant_address", "restaurant_tel", "review_num"], inplace=True)

    df = pd.merge(df_addr, df_type, how="inner", on="restaurant_name")
    df = pd.merge(df, df_ratio, how="inner", on="restaurant_name")
    df.to_csv("Database/data/data.csv", index=False)

def preprocess_pipeline():
    """
    run Pipeline from Crawled Data(Database/raw/*.csv)
    """
    pipelines = [
        raw_csvs_to_integrated_raw_csv,
        add_lat_lon_to_integrated_raw_csv,
        classify_restaurant_type_to_integrated_raw_csv,
        calc_review_ratio_to_integrated_raw_csv,
        integrated_raw_csv_to_data_csv,
    ]
    for p in pipelines:
        p()
        time.sleep(1)

def get_data() -> pd.DataFrame:
    data = pd.read_csv("Database/data/data.csv")
    return data
