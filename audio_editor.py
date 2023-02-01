"""
### audio_editor
语音编辑，切分音频，去除语音中的较长静音，去除语音首尾静音，设置采样率，设置通道数。
音频格式相互转换，例如wav格式转为mp3格式。
切分音频，去除静音，去除首尾静音输入输出都支持wav格式。
语音编辑功能基于pydub的方法，增加了数据格式支持。
"""
import contextlib
import wave
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(Path(__file__).stem)

from pydub import AudioSegment
from pydub.silence import detect_nonsilent

from audio_io import anything2bytesio, _sr, _int16_max
import numpy as np
import io


def convert_channels(wav, sr=_sr, value=1):
    aud = wav2audiosegment(wav, sr=sr)
    aud = aud.set_channels(channels=value)
    wav = audiosegment2wav(aud)
    return wav


def convert_sample_rate(wav, sr=_sr, value=_sr):
    aud = wav2audiosegment(wav, sr=sr)
    aud = aud.set_frame_rate(frame_rate=value)
    wav = audiosegment2wav(aud)
    return wav


def convert_sample_width(wav, sr=_sr, value=4):
    aud = wav2audiosegment(wav, sr=sr)
    aud = aud.set_sample_width(sample_width=value)
    wav = audiosegment2wav(aud)
    return wav

def wav_time(self):
    '''
    获取音频文件是时长
    :param wav_path: 音频路径
    :return: 音频时长 (单位秒)
    '''
    with contextlib.closing(wave.open(self.wav_path, 'r')) as f:
        frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
    return duration

def get_ms_part_wav(self, start_time, end_time, part_wav_path):
    '''
    音频切片，获取部分音频 单位是毫秒级别
    :param self.wav_path: 原音频文件路径
    :param start_time:  截取的开始时间 start_time = 13950
    :param end_time:  截取的结束时间 end_time = 15200
    :param part_wav_path:  截取后的音频路径
    :return:
    '''
    start_time = int(start_time)
    end_time = int(end_time)
    sound = AudioSegment.from_wav(self.wav_path)
    word = sound[start_time:end_time]
    word.export(part_wav_path, format="wav")

def get_second_part_wav(self, start_time, end_time, part_wav_path):
    '''
    音频切片，获取部分音频 单位是秒级别
    :param self.wav_path: 原音频文件路径
    :param start_time:  截取的开始时间 start_time = 35
    :param end_time:  截取的结束时间 end_time = 38
    :param part_wav_path:  截取后的音频路径
    :return:
    '''
    start_time = int(start_time) * 1000
    end_time = int(end_time) * 1000
    sound = AudioSegment.from_wav(self.wav_path)
    word = sound[start_time:end_time]
    word.export(part_wav_path, format="wav")

def get_minute_part_wav(self, start_time, end_time, part_wav_path):
    '''
    音频切片，获取部分音频 分钟:秒数  时间样式："12:35"
    :param self.wav_path: 原音频文件路径
    :param start_time:  截取的开始时间 start_time = "0:35"
    :param end_time:  截取的结束时间 end_time = "0:38"
    :param part_wav_path:  截取后的音频路径
    :return:
    '''
    start_time = (int(start_time.split(':')[0])*60+int(start_time.split(':')[1]))*1000
    end_time = (int(end_time.split(':')[0])*60+int(end_time.split(':')[1]))*1000
    sound = AudioSegment.from_mp3(self.wav_path)
    word = sound[start_time:end_time]
    word.export(part_wav_path, format="wav")

def wav_to_pcm(self, pcm_path):
    '''
    wav文件转为pcm文件
    :param self.wav_path:wav文件路径
    :param pcm_path:要存储的pcm文件路径
    :return: 返回结果
    '''
    f = open(self.wav_path, "rb")
    f.seek(0)
    f.read(44)
    data = np.fromfile(f, dtype=np.int16)
    data.tofile(pcm_path)

def pcm_to_wav(self, pcm_path):
    '''
    pcm文件转为wav文件
    :param pcm_path: pcm文件路径
    :param self.wav_path: wav文件路径
    :return:
    '''
    f = open(pcm_path,'rb')
    str_data  = f.read()
    wave_out=wave.open(self.wav_path,'wb')
    wave_out.setnchannels(1)
    wave_out.setsampwidth(2)
    wave_out.setframerate(8000)
    wave_out.writeframes(str_data)


def convert_format(wav, sr=_sr, format='mp3'):
    """
    语音信号转为指定音频格式的bytes。
    :param wav:
    :param sr:
    :param format:
    :return:
    """
    aud = wav2audiosegment(wav, sr=sr)
    out = io.BytesIO()
    aud.export(out, format=format)
    return out.getvalue()


def convert_format_os(inpath, outpath, out_format='mp3', in_format=None):
    """
    音频格式转换。
    :param inpath:
    :param outpath:
    :param in_format:
    :param out_format:
    :return:
    """
    src = AudioSegment.from_file(inpath, format=in_format)
    src.export(outpath, format=out_format)


def audiosegment2wav(data: AudioSegment):
    """
    pydub.AudioSegment格式转为音频信号wav。
    :param data:
    :return:
    """
    wav = np.array(data.get_array_of_samples()) / _int16_max
    return wav


def wav2audiosegment(wav: np.ndarray, sr):
    """
    音频信号wav转为pydub.AudioSegment格式。
    :param wav:
    :param sr:
    :return:
    """
    tmp = anything2bytesio(wav, sr=sr)
    out = AudioSegment.from_wav(tmp)
    return out


def strip_silence_wave(wav: np.ndarray, sr=_sr, keep_silence_len=20, min_silence_len=100, silence_thresh=-32, **kwargs):
    """
    去除语音前后静音。
    :param wav:
    :param sr:
    :param keep_silence_len:
    :param min_silence_len:
    :param silence_thresh:
    :param kwargs:
    :return:
    """
    data = wav2audiosegment(wav, sr=sr)
    out = strip_audio(data,
                      keep_silence_len=keep_silence_len,
                      min_silence_len=min_silence_len,
                      silence_thresh=silence_thresh,
                      **kwargs)
    out = audiosegment2wav(out)
    return out


def strip_audio(data: AudioSegment, keep_silence_len=20, min_silence_len=100, silence_thresh=-32, **kwargs):
    nsils = detect_nonsilent(data, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    if len(nsils) >= 1:
        return data[max(0, nsils[0][0] - keep_silence_len): min(len(data), nsils[-1][1] + keep_silence_len)]
    else:
        return AudioSegment.empty()


def strip_audio_os(inpath, outpath, **kwargs):
    try:
        data = AudioSegment.from_file(inpath, kwargs.get('format', 'wav'))
        out = strip_audio(data, **kwargs)
        out.export(outpath, kwargs.get('format', 'wav'))
    except Exception as e:
        logger.info('Error path: {}'.format(inpath))
        logger.info('Error info: {}'.format(e))


def split_silence_wave(wav, sr=_sr, keep_silence_len=20, min_silence_len=100, silence_thresh=-32, **kwargs):
    """
    根据静音切分音频。
    :param wav:
    :param sr:
    :param keep_silence_len:
    :param min_silence_len:
    :param silence_thresh:
    :param kwargs:
    :return:
    """
    data = wav2audiosegment(wav, sr=sr)
    outs = split_audio(data,
                       keep_silence_len=keep_silence_len,
                       min_silence_len=min_silence_len,
                       silence_thresh=silence_thresh,
                       **kwargs)
    out_wavs = []
    for out in outs:
        wav = audiosegment2wav(out)
        out_wavs.append(wav)
    return out_wavs


def split_audio(data: AudioSegment, keep_silence_len=20, min_silence_len=100, silence_thresh=-32, **kwargs):
    nsils = detect_nonsilent(data, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    if len(nsils) >= 1:
        outs = []
        for ab in nsils:
            out = data[max(0, ab[0] - keep_silence_len): min(len(data), ab[1] + keep_silence_len)]
            outs.append(out)
    else:
        outs = [AudioSegment.empty()]
    return outs


def remove_silence_wave(wav, sr=_sr, keep_silence_len=20, min_silence_len=100, silence_thresh=-32, **kwargs):
    """
    去除音频中的静音段。
    :param wav:
    :param sr:
    :param keep_silence_len:
    :param min_silence_len:
    :param silence_thresh:
    :param kwargs:
    :return:
    """
    data = wav2audiosegment(wav, sr=sr)
    out = remove_silence_audio(data,
                               keep_silence_len=keep_silence_len,
                               min_silence_len=min_silence_len,
                               silence_thresh=silence_thresh,
                               **kwargs)
    out = audiosegment2wav(out)
    return out


def remove_silence_audio(data: AudioSegment, keep_silence_len=20, min_silence_len=100, silence_thresh=-32, **kwargs):
    nsils = detect_nonsilent(data, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    out = AudioSegment.empty()
    sf = 0
    for i, ab in enumerate(nsils):
        si = max(ab[0] - keep_silence_len, sf)
        ei = ab[1] + keep_silence_len
        out = out + data[si: ei]
        sf = ei
    return out


if __name__ == "__main__":
    print(__file__)
