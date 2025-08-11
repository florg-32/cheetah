import os
import numpy as np
from matplotlib import pyplot as plt
from cheetah.stx import CheetaAnnotationFile, find_annotation_files
from cheetah.wav import extract_wav_segment, load_wav_to_mono


def main():
    annotations_files = find_annotation_files("sample")

    ratios = {}

    for annotation in map(CheetaAnnotationFile.from_stxsm_file, annotations_files):
        wavfile = load_wav_to_mono(os.path.join("sample", annotation.file_id))
        for segment in annotation.vocalisations:
            signal = wavfile[segment.start : segment.start + segment.length]
            noise = wavfile[segment.start - 48000 : segment.start]
            ratios[segment] = signal_to_noise_ratio(signal, noise)

    distances = np.unique(list(map(lambda x: x.distance, ratios.keys())))
    ratios_for_distance = {}
    for d in distances:
        ratios_for_distance[d] = list(map(lambda item: item[1], filter(lambda item: item[0].distance == d, ratios.items())))

    for d, stn in ratios_for_distance.items():
        plt.scatter(np.repeat(d, len(stn)), stn)

    medians = list(map(np.nanmedian, ratios_for_distance.values()))
    plt.plot(distances, medians, marker="x", color="red", linewidth=2)

    plt.show()

def signal_to_noise_ratio(signal, noise):
    return root_mean_square(signal) / root_mean_square(noise)


def root_mean_square(signal):
    signal = np.float64(signal)
    return np.sqrt(np.mean(signal ** 2))


if __name__ == "__main__":
    main()
