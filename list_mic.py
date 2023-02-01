"""
### list_mic
查看麦克风信息
"""
import pyaudio

def find_mic():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)  # 打开数据流
    numberdevices = info.get('deviceCount')  # 获取mic数量
    mic_data = []
    for i in range(0,numberdevices):
        if(p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            mic = 'Mic ID: {} - {}'.format(i, p.get_device_info_by_host_api_device_index(0, i).get('name'))
            mic_data.append(mic)
            print(mic)
    return mic_data