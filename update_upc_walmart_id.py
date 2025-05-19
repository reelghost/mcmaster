import pandas as pd

# File paths
merged_path = r'D:\githubProjects\mcmaster\doordash\doordash_merged.csv'
target_path = r'D:\githubProjects\mcmaster\doordash\20042025.csv'
output_path = r'D:\githubProjects\mcmaster\doordash\20042025_updated.csv'

def update_upc_walmart_id(merged_path, target_path, output_path):
    # Read merged file as lookup
    merged_df = pd.read_csv(merged_path, dtype={'prod_id': str, 'upc': str, 'walmart_id': str})
    merged_lookup = merged_df.set_index('prod_id')[['upc', 'walmart_id']]

    # Read target file
    target_df = pd.read_csv(target_path, dtype={'prod_id': str, 'upc': str, 'walmart_id': str})

    # For each row in target, update upc and walmart_id if prod_id found in merged
    def update_row(row):
        prod_id = row['prod_id']
        if prod_id in merged_lookup.index:
            row['upc'] = merged_lookup.at[prod_id, 'upc']
            row['walmart_id'] = merged_lookup.at[prod_id, 'walmart_id']
        return row

    updated_df = target_df.apply(update_row, axis=1)
    updated_df.to_csv(output_path, index=False)
    print(f'Updated file written to {output_path}')

if __name__ == '__main__':
    update_upc_walmart_id(merged_path, target_path, output_path)
