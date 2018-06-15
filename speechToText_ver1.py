from pynput.keyboard import Key, KeyCode, Listener
import pyaudio
import wave
import time

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

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

    def recognize(self):
        print("Recognizing...")
        audio_to_trans = self.fname

        # obtain audio from the microphone
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(audio_to_trans) as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.record(source)

            try:
                #有language參數
                google_result = r.recognize_google(audio,language='en-US')
                print("google : ", google_result)
            except:
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
                ibm_result = r.recognize_ibm(audio,username="6974fcf1-e18d-4635-a6c5-a6f541ba2974",password="SylKxLg5EscF",language='en-US')
                print("ibm : ", ibm_result)
            except:
                ibm_result = "Exception: ibm cannot recognize!"
                print(ibm_result)
                
            try:
                #在網頁裡面改語言
                wit_result = r.recognize_wit(audio,key="E6OJLZUZKLQ5LIIQH44Y6R5LSLWHXKP6")
                print("wit : ", wit_result)
            except:
                wit_result = "Exception: wit cannot recognize!"
                print(wit_result)

            try:
                #每日限額100單位,沒有language參數
                houndify_result = r.recognize_houndify(audio,client_id="ux0OcpCNbi59F-LnFTf8fA==",client_key="3m8lOoYBPVsGPDubKGJY0Ug8m4qZRKpUp05jFEUDBZG6YKhLsbgtM1NMua2VJQq7ZNXJn2bQbfCYxGdFMKmuUA==")
                print("houndify : ", houndify_result)
            except:
                houndify_result = "Exception: houndify cannot recognize!"
                print(houndify_result)

#            try:
                #離線套件,有language參數(要下載模型)
#                sphinx_result = r.recognize_sphinx(audio,language='en-US')
#                print("sphinx : ", sphinx_result)
#            except:
#                sphinx_result ="Exception: sphinx cannot recognize!" 
#                print(sphinx_result)

            results = [google_result, ibm_result, wit_result, houndify_result]
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

    print("Press ESC to start/stop!")

    class MyListener(Listener):

        def __init__(self):
            super(MyListener, self).__init__(on_press = self.on_press)
            self.recording = False

        def on_press(self, key):
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
