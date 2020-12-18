import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import docx2txt
import zipfile
import boto3
from pydub import AudioSegment
import os
import time

region = 'us-east-1'
s3_client = boto3.client('s3', region_name = region)
bucket = 'csye-7245-final-project'
username='aditya'



def main():
	st.title("File Upload Tutorial")
	doc_file = st.file_uploader("Upload Image",multiple_files=True,type=['mp3','wav','zip','txt'])
	if doc_file is not None:
		file_details = {"Filename":doc_file.name,"FileType":doc_file.type,"FileSize":doc_file.size}
		st.write(file_details)
		if doc_file.type == "text/plain":
			st.text(str(doc_file.read(),"utf-8")) 
			raw_text = str(doc_file.read(),"utf-8") 
			st.write(raw_text)
		
		if doc_file.type == "application/x-zip-compressed":
			zf = zipfile.ZipFile(doc_file.name)
			st.write(zf)
			timestr = time.strftime("%Y%m%d-%H%M%S")
			summ_text_f_tmp = username + "compressed" + timestr + '.zip'
			summ_text_f = username + "compressed" + timestr + '.zip'
			with zipfile(summ_text_f_tmp, 'w') as myzip:
				myzip.write(zf)
				myzip.close()
			summy_text_path = 'src/{}'.format(summ_text_f)
			response = s3_client.upload_file(Filename=summ_text_f_tmp, Bucket=bucket, Key=summy_text_path)
			st.write(response)

		if doc_file.type == "audio/mpeg":
			audio_file = open(doc_file.name,"rb")
			audio_bytes = audio_file.read()
			audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)
			timestr = time.strftime("%Y%m%d-%H%M%S")
			summ_text_f_tmp = username + "audio" + timestr + '.wav'
			summ_text_f = username + "audio" + timestr + '.wav'
			with open(summ_text_f_tmp, mode='bx') as f:
				f.write(audio_bytes)
				f.close()
			summy_text_path = 'src/{}'.format(summ_text_f)
			response = s3_client.upload_file(Filename=summ_text_f_tmp, Bucket=bucket, Key=summy_text_path)
			st.write(response)
		
		

			

if __name__ == '__main__':
	main()