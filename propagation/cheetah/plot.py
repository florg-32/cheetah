from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from scipy.io import wavfile

from cheetah.stx import CheetaAnnotationFile, CheetaSegment


def draw_annotated_spectogram(
    axes: plt.Axes, wav_path: str, annotations: CheetaAnnotationFile
):
    _, audio = wavfile.read(wav_path)
    audio = audio[:, 0]
    draw_standard_spectogram(axes, audio, annotations.samplerate)

    for annot in annotations.vocalisations:
        draw_annotation(axes, annot)


def draw_standard_spectogram(axes: plt.Axes, data, Fs=48000):
    axes.specgram(data, NFFT=1024, noverlap=900, Fs=Fs, cmap="magma")


def draw_annotation(axes: plt.Axes, annotation: CheetaSegment, y_pos=4000, **kwargs):
    axes.add_patch(
        Rectangle(
            (annotation.start / 48000, y_pos), annotation.length / 48000, 400, **kwargs
        )
    )
