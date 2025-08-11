# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openpyxl",
#     "pandas",
# ]
# ///

import os
import sys
import pandas as pd

def main():
    if len(sys.argv) < 3:
        print("Usage: uv run merge_excels.py <input folder> <output.xlsx>")
        sys.exit(1)

    source_folder = sys.argv[1]
    files = map(lambda x: source_folder + x, os.listdir(source_folder))
    excels = map(pd.read_excel, files)
    with_id = map(create_unique_id, excels)
    pd.concat(with_id).to_excel(sys.argv[2], index=False)
    
def create_unique_id(df: pd.DataFrame):
    df["id"] = df["Observation id"].str.cat(df["Subject"], sep='_')
    return df

if __name__ == "__main__":
    main()