import json
import pandas as pd
from pathlib import Path
import cloudscraper

scraper = cloudscraper.create_scraper()
# Path to JSON file
json_path = Path('doordash/bd_20250518_042640_0.json')
output_csv = Path('doordash/doordash_merged.csv')

def extract_info(specs):
    upc = ''
    walmart_id = ''
    for spec in specs:
        if spec.get('name') == 'Universal Product Code (UPC check)':
            upc = spec.get('value', '')
        elif spec.get('name') == 'Walmart Item #':
            walmart_id = spec.get('value', '')
    return upc, walmart_id

def main():
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    rows = []
    for obj in data:
        sku = obj.get('sku', '')
        specs = obj.get('specifications', [])
        upc, walmart_id = extract_info(specs)
        # Only write if BOTH upc and walmart_id are present and non-empty
        if upc and walmart_id and str(upc).strip() != '' and str(walmart_id).strip() != '':
            rows.append({'sku': sku, 'upc': upc, 'walmart_id': walmart_id})
        else:
            print(f"Skipped SKU {sku} due to missing UPC or Walmart ID.")
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(output_csv, index=False)
        print(f"Wrote {len(df)} rows to {output_csv}")

        # Send each row to Google Sheets
        url = "https://script.google.com/macros/s/AKfycbx94hnMutkYa7iT_vqyOuFEcuhlA6rPxLNYqsd0PgPphMfdsr0s6-WmdWjOOyE2PRp51Q/exec"
        headers = {"Content-Type": "application/json"}
        for row in rows:
            payload = {
                "msid": row["sku"],
                "upc": row["upc"],
                "walmart_id": row["walmart_id"]
            }
            print(f"\U0001F4E6 Sending to Sheets: {payload}")
            try:
                response = scraper.post(url, headers=headers, json=payload, timeout=12)
                print("Sent to Google Sheets")
            except Exception as err:
                print(f"Script error: {err}")
    else:
        print("No valid rows to write.")

if __name__ == "__main__":
    main()
