from pynput.keyboard import Key, KeyCode, Listener
import string_align
import pyaudio
import wave
import time
import globalvar as gl
import API_keys
import final_result
import os
import weight

ibm_username = gl.get_value("ibm_username")
ibm_password = gl.get_value("ibm_password")
wit_key = gl.get_value("wit_key")
houndify_id = gl.get_value("houndify_id")
houndify_key = gl.get_value("houndify_key")

weight = gl.get_value("weight")
threshold = gl.get_value("threshold")

class Recorder(object):
    #A recorder class for recording audio to a WAV file.
    #Records in mono by default.

    def __init__(self, channels=2, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(Listener):
    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer):

        super(RecordingFile, self).__init__(self.on_press)
        self.key_pressed = False
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None
        self.results = []
        self.no_exception = True

    def on_press(self, key):
        if key == Key.esc:
            self.key_pressed = True

    # def __enter__(self):
    #     return self

    # def __exit__(self, exception, value, traceback):
    #     self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None
		
    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self.no_exception = True
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        print("Recording...", end='')
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            if self.key_pressed == False:
                return in_data, pyaudio.paContinue
            else:
                print("Save!")
                self.stop()
                self.close()
                return in_data, pyaudio.paComplete
        return callback

    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()
        self.results = self.recognize()
        self.write_text(self.results)
        if self.no_exception == True:
            final_result.to_final_result(self.results, weight, threshold, way = 'james', print_mode = True)
        else:
            print("Your voice is not clear enough, please try again!")
        print("Press ESC to start/stop! Or press 'Q' to exit!")

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate*0.9)
        return wavefile

    def recognize(self):
        print("Recognizing...")
        audio_to_trans = self.fname

        # obtain audio from the microphone
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(audio_to_trans) as source:
            r.adjust_for_ambient_noise(source)
            audio = r.record(source)
            print("-------------------------------")

            try:
                #有language參數
                google_result = r.recognize_google(audio,language='en-US')
                if google_result == '':
                    self.no_exception = False
                    google_result = "Exception: google cannot recognize!"
                    print(google_result)
                else:
                    print("google : ", google_result)
            except:
                self.no_exception = False
                google_result = "Exception: google cannot recognize!"
                print(google_result)

#            try:
                #7天試用,有language參數
#                bing_result = r.recognize_bing(audio,key="a6182cf9927b484ba3c5508dcf5d6a77",language='en-US')
#                print("bing : ", bing_result)
#            except:
#                bing_result = "Exception: bing cannot recognize!"
#                print(bing_result)
                
            try:
                #password:b04@NTUIM,有language參數(沒有zh-TW)
                ibm_result = r.recognize_ibm(audio,username=ibm_username,password=ibm_password,language='en-US')
                if ibm_result == '':
                    self.no_exception = False
                    ibm_result = "Exception: ibm cannot recognize!"
                    print(ibm_result)
                else:
                    print("ibm : ", ibm_result)
            except:
                self.no_exception = False
                ibm_result = "Exception: ibm cannot recognize!"
                print(ibm_result)
                
            try:
                #在網頁裡面改語言
                wit_result = r.recognize_wit(audio,key=wit_key)
                if wit_result == '':
                    self.no_exception = False
                    wit_result = "Exception: wit cannot recognize!"
                    print(wit_result)
                else:
                    print("wit : ", wit_result)
            except:
                self.no_exception = False
                wit_result = "Exception: wit cannot recognize!"
                print(wit_result)

            try:
                #每日限額100單位,沒有language參數
                houndify_result = r.recognize_houndify(audio,client_id=houndify_id,client_key=houndify_key)
                if houndify_result == '':
                    self.no_exception = False
                    houndify_result = "Exception: houndify cannot recognize!"
                    print(houndify_result)
                else:
                    print("houndify : ", houndify_result)
            except:
                self.no_exception = False
                houndify_result = "Exception: houndify cannot recognize!"
                print(houndify_result)

#            try:
                #離線套件,有language參數(要下載模型)
#                sphinx_result = r.recognize_sphinx(audio,language='en-US')
#                print("sphinx : ", sphinx_result)
#            except:
#                sphinx_result ="Exception: sphinx cannot recognize!" 
#                print(sphinx_result)
            print("-------------------------------")
            results = [google_result, ibm_result, wit_result]
            return results

    def write_text(self, results):
        text_file = open("speech_content.txt", "a")
        text_file.write("google : %s\n" % results[0])
        #text_file.write("bing : %s\n" % results[1])
        text_file.write("ibm : %s\n" % results[1])
        text_file.write("wit : %s\n" % results[2])
        text_file.write("houndify : %s\n\n" % results[3])
        text_file.close()


def main():
    print("Press ESC to start/stop! Or press 'Q' to exit!")

    class MyListener(Listener):

        def __init__(self):
            super(MyListener, self).__init__(on_press = self.on_press)
            self.recording = False

        def on_press(self, key):
            if key == KeyCode.from_char('q'):
                os._exit(0)
            if key == Key.esc and self.recording == False:
                self.recording = True
                r = Recorder()
                recorder = r.open("test.wav")
                recorder.start()
                print("Speak!")
                recorder.start_recording()

            elif key == Key.esc and self.recording == True:
                self.recording = False
        

    listener = MyListener()
    listener.start()
    listener.join()

if __name__ == "__main__":
    main()
