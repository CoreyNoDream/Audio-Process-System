"""
### record
录制音频
可以为声源定位服务
"""
import pyaudio
import numpy as np
import wave

class Recording():

    def __init__(self, MICID=0, CHUNK=1024, CHANNELS=3, RATE=51200, RECORD_SECONDS=1, WAVE_OUTPUT_FILENAME='output_demo.wav'):
        self.micid = MICID
        self.chunk = CHUNK
        self.format = pyaudio.paInt16
        self.channels = CHANNELS
        self.framerate = RATE
        self.toltime = RECORD_SECONDS
        self.outputname = WAVE_OUTPUT_FILENAME

    def record_run(self):
        try:
            # # 配置对象参数
            # paser = argparse.ArgumentParser(description="Mic ID")  # 创建参数对象
            # paser.add_argument('--mic', type=int, default=-1, help="the ID of mic device")  # 添加参数
            # args = paser.parse_args()  # 解析对象(实例化)

            # 设置数据流格式
            p = pyaudio.PyAudio()  # 初始化
            stream = p.open(format=self.format,  # 指定数据类型
                            channels=self.channels,  # 声道数
                            rate=self.framerate,  # 采样率
                            input=True,  # 输入流
                            frames_per_buffer=self.chunk,  # 每个缓冲区保存帧数（frame）
                            input_device_index=self.micid)  # 输入端

            print('Recording')
            frames = []
            for i in range(0, int(self.framerate / self.chunk * self.toltime)):
                data = stream.read(self.chunk)
                frames.append(data)
                audio_data = np.fromstring(data, dtype=np.short)  # 转numpy获取最大值
                temp = np.max(np.abs(audio_data))  # 显示每8000个的最大数值
                print("Recent Max：", temp)

            print('done recording')
            stream.stop_stream()
            stream.close()
            p.terminate()

            if self.outputname is not None:
                wf = wave.open(self.outputname, 'wb')  # 打开并设置录音文件
                wf.setnchannels(self.channels)  # 设置声道数为单声道
                wf.setsampwidth(p.get_sample_size(self.format))  # 设置采样字节长度
                wf.setframerate(self.framerate)  # 设置总帧数
                wf.writeframes(b''.join(frames))  # 写入bytes格式的音频帧
                wf.close
        except Exception as ex:
            print('record Exception', ex)