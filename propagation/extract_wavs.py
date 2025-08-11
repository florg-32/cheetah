from itertools import repeat
import multiprocessing
from scipy.io import wavfile
from glob import glob
import os
from tkinter import filedialog

from cheetah.stx import CheetaAnnotationFile, Segment, find_annotation_files
from cheetah.wav import extract_wav_segment, load_wav_to_mono


def main():
    root = filedialog.askdirectory(title="Select root directory of annotations")
    output_path = filedialog.askdirectory(
        title="Select output directory", mustexist=False
    )

    os.makedirs(output_path, exist_ok=True)

    wav_filepaths = find_wav_files(root)
    annotation_filepaths = find_annotation_files(root)

    with multiprocessing.Pool() as p:
        p.starmap(
            extract_annotation,
            zip(annotation_filepaths, repeat(wav_filepaths), repeat(output_path)),
        )


def find_wav_files(root: str):
    wav_filepaths = glob(f"{root}/**/*.wav", recursive=True)
    wav_filepaths += glob(f"{root}/**/*.WAV", recursive=True)
    return {os.path.basename(x): x for x in wav_filepaths}


def extract_annotation(
    annotation_file: str, wav_paths: dict[str, str], output_path: str
):
    annotations = CheetaAnnotationFile.from_stxsm_file(annotation_file)
    wav = load_wav_to_mono(wav_paths[annotations.file_id])
    for segment in annotations.segments:
        file_path = f"{output_path}/{segment.id}.wav"
        wavfile.write(
            file_path,
            annotations.samplerate,
            extract_wav_segment(wav, segment),
        )


if __name__ == "__main__":
    main()
