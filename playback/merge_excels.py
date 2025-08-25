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
from tkinter import filedialog


def main():
    if len(sys.argv) < 3:
        input_folder = filedialog.askdirectory(title="Select input folder")
        output = filedialog.asksaveasfilename(title="Select output file", defaultextension=".xlsx")
    else:
        input_folder = sys.argv[1]
        output = sys.argv[2]

    files = map(lambda x: input_folder + x, os.listdir(input_folder))
    excels = map(pd.read_excel, files)
    with_id = map(create_unique_id, excels)
    pd.concat(with_id).to_excel(output, index=False)


def create_unique_id(df: pd.DataFrame):
    # there are some observations where 2 cameras were used. These have _a _b appended to their observation id
    # which should be removed
    df["id"] = df["Observation id"].str.rstrip("_ab").str.cat(df["Subject"], sep="_")
    return df


if __name__ == "__main__":
    main()
