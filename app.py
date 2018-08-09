import wave
import os
from flask import Flask, render_template, request, jsonify
import web_recognize
import globalvar as gl
import weight
from decimal import Decimal

#weight = gl.get_value("weight")
#threshold = gl.get_value("threshold")

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def index():
	return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
	fname = request.form.get('fname')
	blob = request.form.get('data')[22:]

	decode_blob = safe_base64_decode(blob)
	make_wav_file(fname, decode_blob)

	return ""

@app.route('/recog', methods=['POST'])
def recog():
	fname = request.form.get('fname')
	weight = [Decimal(i) for i in request.form.get('weight').split(',')]
	threshold = Decimal(request.form.get('threshold'))
	results, no_exception, exceed_quota = web_recognize.recognize('./audios/' + fname)
	if no_exception == True:
		alignment, recommendation = web_recognize.to_final_result(results, weight, threshold)
		dic = {"results":results, "no_exception":no_exception, "exceed_quota":exceed_quota, "alignment":alignment, "recommendation":recommendation}
	else:
		if exceed_quota == True:
			del results[-1]
			alignment, recommendation = web_recognize.to_final_result(results, weight, threshold)
			dic = {"results":results, "no_exception":no_exception, "exceed_quota":exceed_quota, "alignment":alignment, "recommendation":recommendation}
		else:
			dic = {"no_exception":no_exception}

	return jsonify(dic)

@app.route('/deleteAudios', methods=['POST'])
def deleteAudios():
	fnames = request.form.getlist('fnames')
	for fname in fnames:
		os.remove('./audios/' + fname)
	return ""


def safe_base64_decode(base64str):
	import base64
	if len(base64str) % 4 == 0:
		decode_base64str = base64.urlsafe_b64decode(base64str)
		return decode_base64str
	else:
		decode_base64str = base64.urlsafe_b64decode(base64str + '=' * (4-len(base64str) % 4))
		return decode_base64str

def make_wav_file(fname, decode_base64str):
	channels = 2
	sampwidth = 2
	rate = 44100   
	
	wavefile = wave.open('./audios/' + fname, 'wb')
	wavefile.setnchannels(channels)
	wavefile.setsampwidth(sampwidth)
	wavefile.setframerate(rate)
	wavefile.writeframes(decode_base64str)


if __name__ == "__main__":
	app.run()
