# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openpyxl",
#     "pandas",
# ]
# ///

import sys
import pandas as pd
from tkinter import filedialog


def main():
    if len(sys.argv) < 3:
        input_file = filedialog.askopenfilename(title="Select input")
        output_file = filedialog.asksaveasfilename(title="Select output file")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]

    df = pd.read_excel(input_file)
    df.pivot_table(index="id", columns="Behavior", aggfunc="size", fill_value=0).reset_index().to_excel(output_file)


if __name__ == "__main__":
    main()
