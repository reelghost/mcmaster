import os
import pandas as pd
from pathlib import Path

def merge_csv_files(folder_path):
    # Convert to Path object for better path handling
    base_path = Path(folder_path)
    
    # Get all subdirectories
    subdirectories = [d for d in base_path.iterdir() if d.is_dir()]
    
    for subdir in subdirectories:
        print(f"\nProcessing directory: {subdir.name}")
        
        # Get all CSV files in the subdirectory
        csv_files = list(subdir.glob('*.csv'))
        
        if not csv_files:
            print(f"No CSV files found in {subdir.name}")
            continue
        
        # List to store DataFrames
        dfs = []
        
        # Read each CSV file
        for csv_file in csv_files:
            try:
                print(f"Reading file: {csv_file.name}")
                df = pd.read_csv(csv_file)
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {csv_file.name}: {str(e)}")
                continue
        
        if not dfs:
            print(f"No valid CSV files found in {subdir.name}")
            continue
        
        # Combine all DataFrames
        merged_df = pd.concat(dfs, ignore_index=True)
        
        # Remove duplicates
        original_rows = len(merged_df)
        merged_df = merged_df.drop_duplicates()
        removed_rows = original_rows - len(merged_df)
        
        # Create output filename using subdirectory name
        output_file = base_path / f"{subdir.name}_merged.csv"
        
        # Save merged DataFrame
        merged_df.to_csv(output_file, index=False)
        print(f"Created merged file: {output_file}")
        print(f"Removed {removed_rows} duplicate rows")
        print(f"Final row count: {len(merged_df)}")

def main():
    # Get the doordash folder path
    script_dir = Path(__file__).parent
    doordash_path = script_dir / "doordash"
    
    if not doordash_path.exists():
        print(f"Error: DoorDash folder not found at {doordash_path}")
        return
    
    print(f"Starting CSV merge process in: {doordash_path}")
    merge_csv_files(doordash_path)
    print("\nMerge process completed!")

if __name__ == "__main__":
    main()
