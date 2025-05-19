from apify_client import ApifyClient
import pandas as pd
from pathlib import Path
import requests
import time
import sys
import random
import json
import os

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_dClRG14DwN0PPS6SeqmZO8nq3Qdtbi0UyNQo")


# def get_product_info(msid):
#     try:
#         run_input = { "productUrls": [f"{msid}"] }
#         run = client.actor("p6rc6x5tzInzsofI6").call(run_input=run_input)
#         c_data = client.dataset(run["defaultDatasetId"]).iterate_items()
#         for item in c_data:
#             print(f"DEBUG: {item}")
#             upc = item.get("UPC")
#             walmart_id = item.get("walmart_id")
#             if upc or walmart_id:
#                 return upc, walmart_id
#         # If for loop completes with no return
#         return None, None
#     except Exception as e:
#         print(f"\nError getting product info for MSID {msid}: {str(e)}")
#         return None, None


def get_product_info(msid):
    try:
        wal_api = f"https://walmart-scraper-api.fly.dev/walmart/{msid}"
        wal_response = requests.get(wal_api)
        print(wal_response.text)
        upc = wal_response.json().get("upc")
        walmart_id = wal_response.json().get("walmart_id")

        if upc or walmart_id:
            return upc, walmart_id
        else:
            time.sleep(random.randint(1, 2))
            return None, None
    except Exception as e:
        print(f"\nError getting product info for MSID {msid}: {str(e)}")
        time.sleep(random.randint(1, 3))
        return None, None


def process_csv_files():
    doordash_path = Path("doordash")

    try:
        merged_files = list(doordash_path.glob("*_merged.csv"))

        for file_path in merged_files:
            print(f"\nProcessing file: {file_path.name}")

            df = pd.read_csv(file_path)

            # Ensure upc and walmart_id columns exist and are of object (string) dtype
            if 'upc' not in df.columns:
                df['upc'] = pd.Series([None]*len(df), dtype='object')
            else:
                df['upc'] = df['upc'].astype('object')
            if 'walmart_id' not in df.columns:
                df['walmart_id'] = pd.Series([None]*len(df), dtype='object')
            else:
                df['walmart_id'] = df['walmart_id'].astype('object')

            rows_to_process = df[
                (df['upc'].isna() | (df['upc'] == '')) &
                (df['walmart_id'].isna() | (df['walmart_id'] == ''))
            ].index

            total_rows = len(rows_to_process)
            if total_rows == 0:
                print(
                    f"All items in {file_path.name} already have UPC and Walmart ID data. Skipping...")
                continue

            print(f"Found {total_rows} items without UPC/Walmart ID data")

            for idx, row_idx in enumerate(rows_to_process):
                msid = str(df.loc[row_idx, 'msid'])
                print(f"\nProcessing item {idx + 1}/{total_rows}: MSID {msid}")

                upc, walmart_id = get_product_info(msid)
                print(f"From api {upc} {walmart_id}")

                # Only write if BOTH upc and walmart_id are present and non-empty
                if upc is not None and walmart_id is not None and str(upc).strip() != '' and str(walmart_id).strip() != '':
                    df.loc[row_idx, 'upc'] = str(upc)
                    df.loc[row_idx, 'walmart_id'] = str(walmart_id)
                    print(f"Found - UPC: {upc}, Walmart ID: {walmart_id}")

                    # Save after every processed row
                    df.to_csv(file_path, index=False)
                    print(f"Progress saved after processing MSID {msid}")
                else:
                    print(f"Skipped MSID {msid} due to missing UPC or Walmart ID.")

            print(f"\nCompleted processing {file_path.name}")

    except Exception as e:
        print(f"\nError processing files: {str(e)}")


if __name__ == "__main__":
    process_csv_files()
