# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openpyxl",
#     "pandas",
# ]
# ///

import sys
import pandas as pd

def main():
    df = pd.read_excel(sys.argv[1])
    df.pivot_table(index="id", columns="Behavior", aggfunc="size", fill_value=0).reset_index().to_excel(sys.argv[2])

if __name__ == "__main__":
    main()