# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openpyxl",
#     "pandas",
# ]
# ///

import pandas as pd
import sys
from tkinter import filedialog


def main():
    if len(sys.argv) < 4:
        playback_plan_path = filedialog.askopenfilename(title="Select playback plan")
        merge_path = filedialog.askopenfilename(title="Select file to merge it with")
        output_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    else:
        playback_plan_path = sys.argv[1]
        merge_path = sys.argv[2]
        output_path = sys.argv[3]

    playback_plan = pd.read_excel(playback_plan_path)
    merge = pd.read_excel(merge_path)

    experiment_number = playback_plan["experiment number"].astype(int).map("{:02d}".format)
    date = pd.to_datetime(playback_plan["date"], dayfirst=False).dt.strftime("%d.%m.%Y")
    playback_plan["Observation id"] = experiment_number.str.cat(date, sep="_")

    joined = merge.set_index("Observation id").join(playback_plan.set_index("Observation id"), validate="m:1")
    joined.to_excel(output_path)


if __name__ == "__main__":
    main()
