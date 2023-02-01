"""
### audio_tuner
语音调整，调整语速，调整音高。
"""
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(Path(__file__).stem)

from pydub import AudioSegment
from scipy.io import wavfile
import numpy as np
import io
from audio_io import anything2bytesio, anything2wav
from audio_io import _sr

import librosa


def smooth(data: np.ndarray, box=3):
    """平滑处理。"""
    if isinstance(box, int):
        box = np.ones(box) / box

    if len(data.shape) == 1:
        out = np.convolve(data, box, mode='same')
        return out
    else:
        out = []
        for vec in data.T:
            out.append(np.convolve(vec, box, mode='same'))
        return np.asarray(out).T
        # 矩阵展开计算和循环计算速度相差很小
        # data_pad = np.zeros((len(box), data.shape[1]))
        # data_tmp = np.vstack((data_pad, data, data_pad)).T.flatten()
        # data_tmp = np.convolve(data, box, mode='same')
        # data_tmp.reshape((data.shape[1], data.shape[0] + 2 * len(box)))
        # out = data_tmp.T[len(box): -len(box)]
        # return out


def zoom(data, rate, is_same=0, pad_value=0):
    """伸缩处理"""
    idx_lst = (np.arange(int(len(data) * rate)) / rate).astype(int)
    if is_same:
        if len(idx_lst) > len(data):
            idx_lst = idx_lst[:len(data)]
            return data[idx_lst]
        elif len(idx_lst) < len(data):
            if len(data.shape) == 1:
                return np.pad(data[idx_lst], (0, len(data) - len(idx_lst)), contant_values=pad_value)
            else:
                data_pad = pad_value * np.ones((len(data) - len(idx_lst), data.shape[1]), dtype=data.dtype)
                return np.vstack((data[idx_lst], data_pad))
        else:
            return data[idx_lst]
    else:
        return data[idx_lst]


def roll(data, num, is_pad=0, pad_value=0):
    """移动处理"""
    tmp = np.roll(data, num)
    if is_pad:
        if num > 0:
            tmp[:num] = pad_value
        elif num < 0:
            tmp[num:] = pad_value
    return tmp


def tune_speed_librosa(src=None, sr=_sr, rate=1., out_type=np.ndarray):
    """
    变语速
    :param src:
    :param rate:
    :return:
    """
    wav = anything2wav(src, sr=sr)
    spec = librosa.stft(wav)
    spec = zoom(spec.T, rate=1 / rate, is_same=0).T
    out = librosa.istft(spec)
    # out = librosa.griffinlim(spec, n_iter=10)
    if out_type is np.ndarray:
        return out
    else:
        return anything2bytesio(out, sr=sr)


def tune_pitch_librosa(src=None, sr=_sr, rate=1., out_type=np.ndarray):
    """
    变音调
    :param src:
    :param rate:
    :return:
    """
    wav = anything2wav(src, sr=sr)
    wav = zoom(wav, rate=1 / rate)
    spec = librosa.stft(wav)
    spec = zoom(spec.T, rate=rate, is_same=0).T
    out = librosa.istft(spec)
    # out = librosa.griffinlim(spec, n_iter=10)
    if out_type is np.ndarray:
        return out
    else:
        return anything2bytesio(out, sr=sr)


tune_speed = tune_speed_librosa
tune_pitch = tune_pitch_librosa


def tune_speed_pydub(src=None, sr=_sr, rate=1., out_type=np.ndarray):
    """
    变语速
    rate = win / (bar - cro)
    :param src:
    :param rate:
    :return:
    """
    song = AudioSegment.from_wav(anything2bytesio(src, sr=sr))
    n_song = len(song)
    win = 50
    bar = 100
    cro = int(bar - win / rate)

    segs = []
    for i in range(0, n_song - bar, win):
        segs.append(song[i: i + bar])

    out_song = segs[0]
    for seg in segs[1:]:
        out_song = out_song.append(seg, cro)

    io_out = io.BytesIO()
    out_song.export(io_out, format="wav")

    if out_type is np.ndarray:
        return anything2wav(io_out.getvalue(), sr=sr)
    else:
        return anything2bytesio(io_out.getvalue(), sr=sr)


def tune_pitch_pydub(src=None, sr=_sr, rate=1., out_type=np.ndarray):
    """
    变音调
    :param io_in:
    :param rate:
    :return:
    """
    frate, wavdata = wavfile.read(anything2bytesio(src, sr=sr))

    cho_ids = [int(w) for w in np.arange(0, len(wavdata), rate)]
    out_wavdata = wavdata[cho_ids]

    io_out = io.BytesIO()
    wavfile.write(io_out, frate, out_wavdata)
    io_out = tune_speed(io_out, rate=1 / rate, out_type=io.BytesIO)
    if out_type is np.ndarray:
        return anything2wav(io_out.getvalue(), sr=sr)
    else:
        return anything2bytesio(io_out.getvalue(), sr=sr)


if __name__ == "__main__":
    print(__file__)
