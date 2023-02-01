import io
import pylab as plt
import numpy as np
import wave
from PIL import Image



class data():
    def __init__(self, wav_path):
        '''
        获取音频信息
        :param wav_path: 音频路径
        [1, 2, 8000, 51158, 'NONE', 'not compressed']
        对应关系：声道，采样宽度，帧速率，帧数，唯一标识，无损
        '''
        self.wav_path = wav_path
        self.nchannels, \
        self.sampwidth, \
        self.framerate, \
        self.nframes, \
        self.str_data = read_wav(self.wav_path)

    def wave_diagram(self):
        '''音频对应的波形图'''
        wave_data = np.fromstring(self.str_data, dtype=np.int16)  # 将波形数据转换成数组
        wave_data.shape = -1, self.nchannels  # 将wave_data数组改为1列(单声道)，行数自动匹配。在修改shape的属性时，需使得数组的总长度不变。
        wave_data = wave_data.T  # 转置数据
        time = np.arange(0, self.nframes)/(1.0/self.framerate)  # 通过取样点数和取样频率计算出每个取样的时间。
        plt.figure(1)
        plt.plot(time, wave_data[0])  # time 也是一个数组，与wave_data[0]或wave_data[1]配对形成系列点坐标
        plt.xlabel("time")
        plt.ylabel("Amplitude")
        plt.title("Single Channel Wavedata")
        plt.grid('on')
        plt.show()
        # plt.subplot(5,1,1)
        # plt.plot(time,waveData[:,0])
        # plt.xlabel("Time(s)")
        # plt.ylabel("Amplitude")
        # plt.title("Ch-1 wavedata")
        # plt.grid('on')
        # plt.plot(time,waveData[:,1])
        # plt.xlabel("Time(s)")
        # plt.ylabel("Amplitude")
        # plt.title("Ch-2 wavedata")
        # plt.grid('on')

    def signal_framing(self, wlen):
        # wlen = 512
        inc = 128  # 帧移
        wave_data = np.fromstring(self.str_data, dtype=np.int16)
        print(wave_data[:10])
        wave_data = wave_data*1.0/(max(abs(wave_data)))
        print(wave_data[:10])
        time = np.arange(0, wlen) * (1.0 / self.framerate)
        signal_length = len(wave_data)  # 信号总长度
        if signal_length <= wlen:  # 若信号长度小于一个帧的长度，则帧数定义为1
            nf = 1
        else:  # 否则，计算帧的总长度
            nf = int(np.ceil((1.0*signal_length-wlen+inc)/inc))
        pad_length = int((nf-1)*inc+wlen)  # 所有帧加起来总的铺平后的长度
        zeros = np.zeros((pad_length-signal_length,))  # 不够的长度使用0填补，类似于FFT中的扩充数组操作
        pad_signal = np.concatenate((wave_data, zeros))  # 填补后的信号记为pad_signal
        indices = np.tile(np.arange(0, wlen), (nf, 1))+np.tile(np.arange(0, nf*inc, inc), (wlen, 1)).T  # 相当于对所有帧的时间点进行抽取，得到nf*nw长度的矩阵
        print(indices[:2])
        indices = np.array(indices, dtype=np.int32)  # 将indices转化为矩阵
        frames = pad_signal[indices]  # 得到帧信号
        a = frames[30:31]
        print(a[0])
        plt.figure(figsize=(10,4))
        plt.plot(time, a[0], c="g")
        plt.grid()
        plt.show()


def read_wav(wav_path):
    with wave.open(wav_path, "rb") as f:
        '''
        读取音频文件内容
        :param wav_path: 音频路径
        :return: 音频内容
        '''
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes, str_data = params[:5]
        # 读取声音数据，传递一个参数指定需要读取的长度（以取样点为单位）
        str_data = f.readframes(nframes)

    return nchannels, sampwidth, framerate, nframes, str_data


def draw_sound_wave(wav, sr=16000, width=300, height=100):
    try:
        x_axis = np.arange(wav.shape[0])/sr
        fig = plt.figure("Image", frameon=False, figsize=(width/100, height/100))
        plt.clf()
        plt.cla()
        canvas = fig.canvas
        plt.axis('off')
        plt.plot(x_axis, wav)
        buffer = io.BytesIO()
        canvas.print_png(buffer)
        img_data = buffer.getvalue()
        buffer.write(img_data)
        img = Image.open(buffer).convert('RGB')
        img = np.asarray(img)
        plt.close()
        return img
    except Exception as ex:
        print("draw_sound_wave ", ex)
