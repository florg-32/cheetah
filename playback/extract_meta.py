from functools import partial
from glob import glob
import pandas as pd
from tkinter import filedialog, messagebox
from os import path

from cheetah.stx import CheetaAnnotationFile, find_annotation_files


def main():
    root = filedialog.askdirectory(title="Select root directory of annotations")
    output_file = filedialog.asksaveasfilename(
        title="Save as",
        filetypes=[("Excel file", ".xlsx"), ("Comma-separated values", ".csv")],
        defaultextension=".xlsx",
    )

    _, extension = path.splitext(output_file)
    if extension not in [".xlsx", ".csv"]:
        messagebox.showerror("Invalid file extension")
        exit(1)

    annotation_filepaths = find_annotation_files(root)

    wav_names = map(lambda x: CheetaAnnotationFile.from_stxsm_file(x).file_id, annotation_filepaths)
    dataframes = list(map(partial(pd.read_xml, parser="etree"), annotation_filepaths))
    for df, wav in zip(dataframes, wav_names):
        df.insert(0, "WAV File", wav)


    output_frame = pd.concat(dataframes)

    if extension == ".xlsx":
        output_frame.to_excel(output_file, index=False)
    elif extension == ".csv":
        output_frame.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()
