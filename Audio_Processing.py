from pathlib import Path
import librosa
from PyQt5.QtGui import QImage, QPixmap
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(Path(__file__).stem)
import Ui_AudioProcess
import audio_changer as ch
import audio_data as data
import audio_denoise as de
import audio_editor as ed
import audio_io as io
import audio_normalizer as no
import audio_player as play
# import audio_tuner
# import audio_world
import database
import list_mic
import record as re
import audio_localization as al
import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog



class mywindow(QDialog):
    def __init__(self, parent=None):
        try:
            super(QDialog, self).__init__(parent)
            self.ui = Ui_AudioProcess.Ui_AudioProcess()
            self.ui.setupUi(self)
            self.db = None
            self.wav = None
            self.sr = None
        except Exception as ex:
            print('initial Exception', str(ex))


    def data(self):
        """Display audio data"""
        try:
            path = w.ui.inputlineEdit.text()
            d = data.data(wav_path=path)
            self.wav, self.sr = librosa.load(path)
            w.list_show('channels:{}  samplewidth:{}  framerate:{}  nframes:{}'.format(d.nchannels, d.sampwidth, d.framerate, d.nframes))
            self.oscillogram()
        except Exception as ex:
            w.list_show('data Exception')
            w.list_show(str(ex))
            print('data Exception', str(ex))


    def io_save_wav(self):
        """Sava audio"""
        try:
            input_file = self.ui.inputlineEdit.text()
            output_file = self.ui.outputFilelineEdit.text()
            name = os.path.split(input_file)[-1]
            save_name = '{}/{}'.format(output_file, name)
            io.save_wav(wav=self.wav, sr=self.sr, path=save_name)
            w.list_show(save_name)
        except Exception as ex:
            w.list_show('save Exception')
            w.list_show(str(ex))
            print('save Exception', str(ex))


    def list_show(self, stat):
        """Interaction"""
        try:
            self.ui.list.moveCursor(self.ui.list.textCursor().End)  # 文本框显示到底
            self.ui.list.ensureCursorVisible()  # 显示最后一条数据
            self.ui.list.append(stat)  # 添加文字
            self.ui.cursor = self.ui.list.textCursor()
            self.ui.list.moveCursor(self.ui.list.textCursor().End)
            QtWidgets.QApplication.processEvents()  # 去卡顿
        except Exception as ex:
            print('list Exception')


    def oscillogram(self):
        """Audio oscillogram"""
        try:
            osc = data.draw_sound_wave(wav=self.wav, width=self.ui.oscillogram.width(), height=self.ui.oscillogram.height())
            temp_osc = QImage(osc, osc.shape[1], osc.shape[0],osc.shape[1]*3, QImage.Format_RGB888)
            label_width = self.ui.oscillogram.width()
            label_height = self.ui.oscillogram.height()
            pixmap_osc = QPixmap.fromImage(temp_osc).scaled(label_width, label_height)
            self.ui.oscillogram.setPixmap(pixmap_osc)
        except Exception as ex:
            w.list_show('oscillogram Exception')
            w.list_show(str(ex))
            print('oscillogram Exception', str(ex))


    def show_mic(self):
        """Show mic info"""
        try:
            mic = list_mic.find_mic()
            for i in mic:
                w.list_show(i)
        except Exception as ex:
            w.list_show('mic Exception')
            w.list_show(str(ex))
            print('Exception', str(ex))


    def play(self):
        """Play audio data"""
        try:
            w.list_show('play')
            play.play_sound(src=self.wav, sr=self.sr)
            w.list_show('end')
        except Exception as ex:
            w.list_show('play Exception')
            w.list_show(str(ex))
            print('Exception', str(ex))


    def record(self):
        """Record audio for audio localization"""
        try:
            MICID = int(self.ui.micidRecordlineEdit.text())
            CHUNK = int(self.ui.chunkRecordlineEdit.text())
            CHANNELS = int(self.ui.channelsRecordlineEdit.text())
            RATE = int(self.ui.rateRecordlineEdit.text())
            RECORD_SECONDS = int(self.ui.timeRecordlineEdit.text())
            WAVE_OUTPUT_FILENAME = self.ui.outputlineEdit.text()
            r = re.Recording(MICID=MICID,
                             CHUNK=CHUNK,
                             CHANNELS=CHANNELS,
                             RATE=RATE,
                             RECORD_SECONDS=RECORD_SECONDS,
                             WAVE_OUTPUT_FILENAME=WAVE_OUTPUT_FILENAME)
            w.list_show('Start Recording')
            w.list_show('micID:{}, chunk:{}, channels:{}, rate:{}, time:{}'
                        .format(MICID, CHUNK, CHANNELS, RATE, RECORD_SECONDS))
            r.record_run()
        except Exception as ex:
            w.list_show('record Exception')
            w.list_show(str(ex))
            print('record Exception', str(ex))
    def sound_localization(self):
        """Sound localization"""
        try:
            input_wav = self.ui.inputlineEdit.text()
            output_h5 = self.ui.outputlineEdit.text()
            al.toHDF5(input_wav, output_h5)
            al.sound_localization(input_h5=output_h5)
            self.ui.cartesianGrid.setPixmap(QPixmap('beamforming cartesian 2D grid.png'))
        except Exception as ex:
            w.list_show('location Exception')
            w.list_show(str(ex))
            print('location Exception', str(ex))


    def config_db(self):
        """Configure database"""
        try:
            host = self.ui.hostDblineEdit.text()
            user = self.ui.userDblineEdit.text()
            passwd = self.ui.pswdDblineEdit.text()
            dbname = self.ui.NameDblineEdit.text()
            port = self.ui.portDblineEdit.text()
            self.db = database.database(host=host, user=user, passwd=passwd, dbname=dbname, port=port)
            w.list_show('Configure database {} successfully'.format(dbname))
        except Exception as ex:
            w.list_show('config Exception')
            w.list_show(str(ex))
            print('config Exception', str(ex))
    def table_db(self):
        """Creat table"""
        try:
            table = self.ui.tableDblineEdit.text()
            table_out = '{}_out'.format(table)
            self.db.create_table(newtable=table)
            self.db.create_table(newtable=table_out)
            w.list_show('Create table {} successfully'.format(table))
        except Exception as ex:
            w.list_show('create Exception')
            w.list_show(str(ex))
            print('create Exception', str(ex))
    def insert_db(self):
        """Insert unprocessed audio"""
        try:
            inputFile = self.ui.inputFilelineEdit.text()
            table = self.ui.tableDblineEdit.text()
            print('open', inputFile)
            files = os.listdir(inputFile)
            for file in files:
                name = file
                site = ('{}/{}'.format(inputFile, name))
                print(name, site, sep=':  ')
                self.db.insert_data(name, site, table)
                w.list_show('{}  {}'.format(name, site))
            w.list_show('complete insert')
        except Exception as ex:
            w.list_show('insert Exception')
            w.list_show(str(ex))
            print('insert Exception', str(ex))
    def process_db(self):
        """Process audio data"""
        try:
            outputFile = self.ui.outputFilelineEdit.text()
            table = self.ui.tableDblineEdit.text()
            idField = self.db.read_data('id', table)
            nameField = self.db.read_data('name', table)
            sitesField = self.db.read_data('sites', table)
            table_out = '{}_out'.format(table)
            w.list_show('Start denoise')
            for x in idField:
                x = int(x)
                name = nameField[x-1]
                site_input = sitesField[x-1]
                print('{} {}: {}'.format(x, name, site_input))
                de.denoise_run(name=name, site_input=site_input, site_output=outputFile)
                self.db.insert_data(name, site_input, table_out)
                w.list_show('{}  {}'.format(name, site_input))
            w.list_show('Finish process')
        except Exception as ex:
            w.list_show('process Exception')
            w.list_show(str(ex))
            print('process Exception')


    def changer_pitch(self):
        """
        Adjust pitch
        rate:-20~20
        """
        try:
            rate = self.ui.pitchverticalSlider.value()
            self.wav = ch.change_pitch(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))
    def changer_speed(self):
        """
        Adjust speed
        rate:0~5
        """
        try:
            rate = self.ui.speedverticalSlider.value()
            self.wav = ch.change_speed(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))
    def changer_sample(self):
        """
        Adjust sample
        rate:0~5
        """
        try:
            rate = self.ui.sampleverticalSlider.value()
            self.wav = ch.change_sample(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))
    def changer_reback(self):
        """
        Adjust reback
        rate:1~10
        """
        try:
            rate = self.ui.rebackverticalSlider.value()
            self.wav = ch.change_reback(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))
    def changer_pitchspeed(self):
        """
        Adjust both pitch and speed
        rate:0~10
        """
        try:
            rate = self.ui.pitchspeedverticalSlider.value()
            self.wav = ch.change_pitchspeed(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))
    def changer_attention(self):
        """
        Enhance high pitch or low pitch
        rate:-100~100
        """
        try:
            rate = self.ui.attentionverticalSlider.value()
            self.wav = ch.change_attention(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))
    def changer_male(self):
        """
        Convert to male
        rate:0~1025
        """
        try:
            rate = self.ui.maleverticalSlider.value()
            self.wav = ch.change_male(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))
    def changer_stretch(self):
        """
        Multiple stretch extension
        rate:1~10
        """
        try:
            rate = self.ui.stretchverticalSlider.value()
            self.wav = ch.change_stretch(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))
    def changer_vague(self):
        """
        Blur he audio
        rate:1~10
        """
        try:
            rate = self.ui.vagueverticalSlider.value()
            self.wav = ch.change_pitch(wav=self.wav, sr=self.sr, rate=rate)
            self.oscillogram()
        except Exception as ex:
            w.list_show('changer Exception')
            w.list_show(str(ex))
            print('changer Exception', str(ex))



    def editor_strip(self):
        """Mute the voice before and after"""
        try:
            keep_silence_len = int(self.ui.keepMutelineEdit.text())
            min_silence_len = int(self.ui.minMutelineEdit.text())
            silence_thresh = int(self.ui.threshMutelineEdit.text())
            self.wav = ed.strip_silence_wave(self.wav,
                                             keep_silence_len=keep_silence_len,
                                             min_silence_len=min_silence_len,
                                             silence_thresh=silence_thresh)
            self.oscillogram()
        except Exception as ex:
            w.list_show('editor Exception')
            w.list_show(str(ex))
            print('editor Exception', str(ex))
    def editor_remove(self):
        """Remove mute segments from audio"""
        try:
            keep_silence_len = int(self.ui.keepMutelineEdit.text())
            min_silence_len = int(self.ui.minMutelineEdit.text())
            silence_thresh = int(self.ui.threshMutelineEdit.text())
            self.wav = ed.remove_silence_wave(self.wav,
                                              keep_silence_len=keep_silence_len,
                                              min_silence_len=min_silence_len,
                                              silence_thresh=silence_thresh)
            self.oscillogram()
        except Exception as ex:
            w.list_show('editor Exception')
            w.list_show(str(ex))
            print('editor Exception', str(ex))
    def editor_split(self):
        """Cut the audio according to the mute"""
        try:
            keep_silence_len = int(self.ui.keepMutelineEdit.text())
            min_silence_len = int(self.ui.minMutelineEdit.text())
            silence_thresh = int(self.ui.threshMutelineEdit.text())
            self.wav = ed.split_silence_wave(self.wav,
                                             keep_silence_len=keep_silence_len,
                                             min_silence_len=min_silence_len,
                                             silence_thresh=silence_thresh)
            self.oscillogram()
        except Exception as ex:
            w.list_show('editor Exception')
            w.list_show(str(ex))
            print('editor Exception', str(ex))
    def editor_channels(self):
        """Edit channels"""
        try:
            channels = int(self.ui.channelsEditlineEdit.text())
            if channels is not None:
                self.wav = ed.convert_channels(wav=self.wav, sr=self.sr, value=channels)
        except Exception as ex:
            w.list_show('editor Exception')
            w.list_show(str(ex))
            print('editor Exception', str(ex))
    def editor_rate(self):
        """Edit rate"""
        try:
            rate = int(self.ui.rateEditlineEdit.text())
            if rate is not None:
                self.wav = ed.convert_sample_rate(wav=self.wav, sr=self.sr, value=rate)
        except Exception as ex:
            w.list_show('editor Exception')
            w.list_show(str(ex))
            print('editor Exception', str(ex))
    def editor_width(self):
        """Edit width"""
        try:
            width = int(self.ui.widthEditlineEdit.text())
            if width is not None:
                self.wav = ed.convert_sample_width(wav=self.wav, sr=self.sr, value=width)
        except Exception as ex:
            w.list_show('editor Exception')
            w.list_show(str(ex))
            print('editor Exception', str(ex))


    def normalizer_remove_silence(self):
        """Unmute the voice"""
        try:
            max_silence_ms = int(self.ui.maxNormalizerlineEdit.text())
            self.wav = no.remove_silence(wav=self.wav, sr=self.sr, max_silence_ms=max_silence_ms)
            self.oscillogram()
        except Exception as ex:
            w.list_show('normalizer Exception')
            w.list_show(str(ex))
            print('normalizer Exception', str(ex))
    def normalizer_tune_volume(self):
        """Adjust the volume"""
        try:
            increase_only = False
            decrease_only = False
            target_dBFS = int(self.ui.targetNormalizerlineEdit.text())
            if self.ui.nomalizercomboBox.currentText() == 'increase_only':
                increase_only = True
            elif self.ui.nomalizercomboBox.currentText() == 'decrease_only':
                decrease_only = True
            self.wav = no.tune_volume(wav=self.wav, target_dBFS=target_dBFS, increase_only=increase_only, decrease_only=decrease_only)
            self.oscillogram()
        except Exception as ex:
            w.list_show('normalizer Exception')
            w.list_show(str(ex))
            print('normalizer Exception', str(ex))


    def input(self):
        directory =QtWidgets.QFileDialog.getOpenFileName(None, 'select file', os.getcwd(), 'All Files(*);;Text Files(*.txt)')
        w.ui.inputlineEdit.setText(directory[0])
        w.list_show(directory[0])

    def output(self):
        directory =QtWidgets.QFileDialog.getOpenFileName(None, 'select file', os.getcwd(), 'All Files(*);;Text Files(*.txt)')
        w.ui.outputlineEdit.setText(directory[0])
        w.list_show(directory[0])

    def inputfile(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, 'select folder')
        w.ui.inputFilelineEdit.setText(directory)
        w.list_show(directory)

    def outputfile(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, 'select folder')
        w.ui.outputFilelineEdit.setText(directory)
        w.list_show(directory)


    def help(self):
        self.oscillogram()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = mywindow()
    w.ui.pitchverticalSlider.sliderPressed.connect(w.changer_pitch)
    w.ui.speedverticalSlider.sliderPressed.connect(w.changer_speed)
    w.ui.sampleverticalSlider.sliderPressed.connect(w.changer_sample)
    w.ui.rebackverticalSlider.sliderPressed.connect(w.changer_reback)
    w.ui.pitchspeedverticalSlider.sliderPressed.connect(w.changer_pitchspeed)
    w.ui.attentionverticalSlider.sliderPressed.connect(w.changer_attention)
    w.ui.maleverticalSlider.sliderPressed.connect(w.changer_male)
    w.ui.stretchverticalSlider.sliderPressed.connect(w.changer_stretch)
    w.ui.vagueverticalSlider.sliderPressed.connect(w.changer_vague)
    w.ui.playButton.clicked.connect(w.play)
    w.ui.inputButton.clicked.connect(w.input)
    w.ui.outputButton.clicked.connect(w.output)
    w.ui.inputFileButton.clicked.connect(w.inputfile)
    w.ui.outputFileButton.clicked.connect(w.outputfile)
    w.ui.openButton.clicked.connect(w.data)
    w.ui.saveButton.clicked.connect(w.io_save_wav)
    w.ui.stripButton.clicked.connect(w.editor_strip)
    w.ui.removeButton.clicked.connect(w.editor_remove)
    w.ui.splitButton.clicked.connect(w.editor_split)
    w.ui.editButton.clicked.connect(w.editor_channels)
    w.ui.editButton.clicked.connect(w.editor_rate)
    w.ui.editButton.clicked.connect(w.editor_width)
    w.ui.configButton.clicked.connect(w.config_db)
    w.ui.creatButton.clicked.connect(w.table_db)
    w.ui.insertButton.clicked.connect(w.insert_db)
    w.ui.denoiseButton.clicked.connect(w.process_db)
    w.ui.micButton.clicked.connect(w.show_mic)
    w.ui.recordButton.clicked.connect(w.record)
    w.ui.muteButton.clicked.connect(w.normalizer_remove_silence)
    w.ui.volumeButton.clicked.connect(w.normalizer_tune_volume)
    w.ui.locationButton.clicked.connect(w.sound_localization)
    w.ui.helpButton.clicked.connect(w.help)
    w.show()
    sys.exit(app.exec_())
