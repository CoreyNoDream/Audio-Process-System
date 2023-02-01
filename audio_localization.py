import io
from PIL import Image
import matplotlib.pylab as plt
import numpy as np
import acoular
import pylab as plt
from os import path
import tables
from scipy.io import wavfile

# acoular： http://www.acoular.org/get_started/index.html
# 频谱使用 Welch方法计算:
# 从信号中提取样本块并使用 FFT进行傅里叶变换，用于计算功率谱，然后将结果在多个块上进行平均
# 这些块具有一定的长度并且可能是重叠的
# 可以在 FFT之前对每个块应用加窗函数

def toHDF5(input_wav, output_h5):
    # 配置文件
    samplerate, data = wavfile.read(input_wav)  # 返回rate和data
    # fs=wave.open(name_+'.wav')
    # 配置采样率
    meh5 = tables.open_file(output_h5, mode='w', title='test file')
    meh5.create_earray('/', 'time_data', obj=data)  # 创建可扩充数组time_data 保存的数组或标量data
    meh5.set_node_attr('/time_data', 'sample_freq', 16000)  # 操作节点time_data设置属性名sample_freq与属性值

def sound_localization(input_h5):
    # 读取Mic位置
    micgeofile = path.join('Mic.xml')  # 输入Mic文件
    mg = acoular.MicGeom(from_file=micgeofile)

    # 创建 HDF5数据并实例化
    ts = acoular.TimeSamples(name=input_h5)
    #  打印 HDF5格式音频 time data
    print('Bytes', ts.numsamples)
    print('Channels', ts.numchannels)
    print('Sample frequency', ts.sample_freq)
    print(ts.data)

    # 绘图
    plt.ion()
    plt.plot(mg.mpos[0], mg.mpos[1], 'o')
    plt.show()
    plt.waitforbuttonpress()
    plt.imsave('Mic position.png', plt)

    env = acoular.Environment(c=346.04)

    # 绘制Mic收音二维网格
    rg = acoular.RectGrid(x_min=-1, x_max=1, y_min=-1, y_max=1, z=0.3, increment=0.01)
    # 使用焦点网格和麦克风安排来计算转向矢量
    # 包含从网格点到麦克风位置的传递函数的权重
    # （用单源传输模型实现转向矢量的基本类）
    st = acoular.SteeringVector(grid=rg, mics=mg, env=env)
    # 分帧加窗 得到多通道时间数据的交叉谱矩阵及其特征分解
    ps = acoular.PowerSpectra(time_data=ts, block_size=128, window='Hanning')

    # 使用转向向量和交叉谱矩阵作为输入数据
    # （波束形成在频域采用基本的延迟求和算法）
    bb = acoular.BeamformerBase(freq_data=ps, steer=st)

    # 计算交叉谱矩阵并执行波束成形
    # 结果（声压平方）以与网格形状相同的数组形式给出
    pm = bb.synthetic(2000, 2)  # 查询频率为2000 Hz、频带超过2倍频程的波束形成结果映射到网格上
    # 转换为分贝
    Lm = acoular.L_p(pm)

    # 绘制结果
    plt.figure()
    plt.imshow(Lm.T, origin='lower', vmin=Lm.max()-0.1, extent=rg.extend())
    plt.colorbar()
    plt.waitforbuttonpress()
    plt.imsave('beamforming cartesian 2D grid.png', plt)
    plt.show()

'''
Source location (relative to array center) and levels:

====== =============== ======
Source Location        Level 
====== =============== ======
1      (-0.1,-0.1,0.3) 1.0 Pa
2      (0.15,0,0.3)    0.7 Pa 
3      (0,0.1,0.3)     0.5 Pa
====== =============== ======
'''





