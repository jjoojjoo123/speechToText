import globalvar as gl
import API_keys

ibm_username = gl.get_value("ibm_username")
ibm_password = gl.get_value("ibm_password")
wit_key = gl.get_value("wit_key")
houndify_id = gl.get_value("houndify_id")
houndify_key = gl.get_value("houndify_key")

store_result = {}

def recognize(AudioFile):
	if AudioFile in store_result:
		result = store_result[AudioFile]
		if result[1] or result[2]: #no_exception or exceed_quota
			return store_result[AudioFile]
		else:
			pass #re-recognize
	audio_to_trans = AudioFile
	no_exception = True
	exceed_quota = False

	# obtain audio from the microphone
	import speech_recognition as sr
	r = sr.Recognizer()
	with sr.AudioFile(audio_to_trans) as source:
		r.adjust_for_ambient_noise(source)
		audio = r.record(source)
		#print("-------------------------------")

		try:
			#有language參數
			google_result = r.recognize_google(audio,language='en-US')
			if google_result == '':
				no_exception = False
				google_result = "Exception: google cannot recognize!"
				#print(google_result)
			else:
				#print("google : ", google_result)
				pass
		except:
			no_exception = False
			google_result = "Exception: google cannot recognize!"
			#print(google_result)

		try:
			#password:b04@NTUIM,有language參數(沒有zh-TW)
			ibm_result = r.recognize_ibm(audio,username=ibm_username,password=ibm_password,language='en-US')
			if ibm_result == '':
				no_exception = False
				ibm_result = "Exception: ibm cannot recognize!"
				#print(ibm_result)
			else:
				#print("ibm : ", ibm_result)
				pass
		except:
			no_exception = False
			ibm_result = "Exception: ibm cannot recognize!"
			#print(ibm_result)
			
		try:
			#在網頁裡面改語言
			wit_result = r.recognize_wit(audio,key=wit_key)
			if wit_result == '':
				no_exception = False
				wit_result = "Exception: wit cannot recognize!"
				#print(wit_result)
			else:
				#print("wit : ", wit_result)
				pass
		except:
			no_exception = False
			wit_result = "Exception: wit cannot recognize!"
			#print(wit_result)

		try:
			#每日限額100單位,沒有language參數
			houndify_result = r.recognize_houndify(audio,client_id=houndify_id,client_key=houndify_key)
			if houndify_result == '':
				no_exception = False
				houndify_result = "Exception: houndify cannot recognize!"
				#print(houndify_result)
			else:
				#print("houndify : ", houndify_result)
				pass
		except:
			if no_exception == True:
				exceed_quota = True
			no_exception = False
			houndify_result = "Exception: houndify cannot recognize!"
			#print(houndify_result)

		#print("-------------------------------")
		results = [google_result, ibm_result, wit_result, houndify_result]
		store_result[AudioFile] = results, no_exception, exceed_quota
		return results, no_exception, exceed_quota