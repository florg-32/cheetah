from scipy.io import wavfile
from cheetah.stx import Segment


def load_wav_to_mono(path: str):
    _, file = wavfile.read(path)
    if file.ndim > 1:  # if there are multiple dimensions (channels) take only the first
        file = file[:, 0]
    return file


def extract_wav_segment(wav_array, segment: Segment, additional=48000):
    start = max(segment.start - additional, 0)
    end = min(segment.start + segment.length + additional, len(wav_array))
    return wav_array[start:end]
