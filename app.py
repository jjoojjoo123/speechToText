import wave
import os
import ssl
from flask import Flask, render_template, request, jsonify
import web_recognize
import final_result
import globalvar as gl
import weight #deprecated
import use_reasoner
from decimal import Decimal

os.chdir(os.path.dirname(os.path.realpath(__file__)))
ssl._create_default_https_context = ssl._create_unverified_context

#weight = gl.get_value("weight")
#threshold = gl.get_value("threshold")

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def index():
	return render_template('index.html')

@app.route('/reasoner_page.html')
def reasoner_page():
	return render_template('reasoner_page.html')

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
	use_stem = (request.form.get('use_stem') == 'T')
	lowercast = (request.form.get('lowercast') == 'T')
	way = request.form.get('way')
	results, no_exception, exceed_quota = web_recognize.recognize('./audios/' + fname)
	if no_exception == True:
		alignment, recommendation = final_result.to_final_result(results, weight, threshold, way = way, use_stem = use_stem, lowercast = lowercast)
		dic = {"results":results, "no_exception":no_exception, "exceed_quota":exceed_quota, "alignment":alignment, "recommendation":recommendation}
	else:
		if exceed_quota == True:
			results = results[:-1]
			alignment, recommendation = final_result.to_final_result(results, weight, threshold, way = way, use_stem = use_stem, lowercast = lowercast)
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
	dirName = 'audios'
	if not os.path.exists(dirName):
		os.mkdir(dirName)

	channels = 2
	sampwidth = 2
	rate = 44100   
	
	with wave.open(f'./{dirName}/{fname}', 'wb') as wavefile:
		wavefile.setnchannels(channels)
		wavefile.setsampwidth(sampwidth)
		wavefile.setframerate(rate)
		wavefile.writeframes(decode_base64str)

@app.route('/saveText', methods=['POST'])
def saveText():
	dirName = 'texts'
	if not os.path.exists(dirName):
		os.mkdir(dirName)

	fname = request.form.get('fname')
	story = request.form.get('story')
	query = request.form.get('query')
	with open(f'./{dirName}/{fname}_story', 'w') as textFile:
		textFile.write(story)
	with open(f'./{dirName}/{fname}_query', 'w') as textFile:
		textFile.write(query)
	result = use_reasoner.run(storypath = f'./{dirName}/{fname}_story', querypath = f'./{dirName}/{fname}_query')

	return jsonify({'result': result})

@app.route('/deleteTexts', methods=['POST'])
def deleteTexts():
	fnames = request.form.getlist('fnames')
	for fname in fnames:
		os.remove('./texts/' + fname + '_story')
		os.remove('./texts/' + fname + '_query')
	return ""

if __name__ == "__main__":
	app.run()