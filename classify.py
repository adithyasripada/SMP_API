#from flask import Flask, request, render_template
from instagetter import worker
from tiktokgetter import get_link_tik
from query import query
from proprocess import preprocess_image
from parsecsv import parse_csv
import csv
import io
import re
import pandas as pd
import requests
import threading
import requests
import base64
from PIL import Image
from io import BytesIO
import imghdr
import requests
from moviepy.editor import VideoFileClip
from PIL import Image
import urllib.request
import streamlit as st
from facebookgetter import get_link_fb

st.title("""Social Media Post Image Classifier""")

file = st.file_uploader("Pick a file")
classarray = ["Male","Female","Both","Unspecified"]
assignedClasses = []

def gettobase64(url):
    response = requests.get(url)
    image_data = response.content
    base64_image = base64.b64encode(image_data).decode('utf-8')
    return base64_image

def classify(file,classarray):
    if file:
        print(file)
        content = parse_csv(file)
        final = ""
        outputClasses = []
        for x in content:
            locallygen = True
            if re.match(r"(?:https?:\/\/)?(?:www\.)?(?:tiktok\.com)\/.*", x):
                locallygen = True
                print("This is a TikTok link.")
                try:
                    path = get_link_tik(x)
                    img = preprocess_image(path)
                    img_buffer = BytesIO()
                    img.save(img_buffer, format="JPEG") 
                    img_buffer.seek(0)
                    image_data = img_buffer.read()
                    image = base64.b64encode(image_data).decode('utf-8')
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    continue 

            elif re.match(r"(?:https?:\/\/)?(?:www\.)?(?:facebook\.com)\/.*", x):
                locallygen = False
                print("This is a Facebook link.")
                try:
                    path = get_link_fb(x)
                    print(requests.get(path).text)
                    if len(requests.get(path).text) < 100:
                        path = None
                    else: image = path
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    continue        
            
            else:
                print("This is a Instagram link.")
                locallygen = True
                try:
                    path = worker(x)
                    image = gettobase64(path)
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    continue

            if path is not None:
                try:
                    print(path)
                    div1 = '<div style="display:flex font-size:20px">'
                    div2 = '</div>'
                    if not locallygen:
                        img = f'<img src="{image}" width="200" height="200">'
                    else:
                        img = f'<img src="data:image/jpeg;base64,{image}" width="200" height="200">'
                    finalclass=query(path, classarray)
                    outputClasses.append({'Image_URL': x, 'GeneratedText': finalclass})
                    line = div1 + img + finalclass + div2 + '<br><br>' 
                    final = final + line  
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    continue
    return final, outputClasses

if st.button("Classify"):
    html_string, assignedClasses = classify(file,classarray)
    st.markdown(html_string, unsafe_allow_html=True)

results_df = pd.DataFrame(assignedClasses)

def convert_df(df):
    return df.to_csv().encode('utf-8')
csv = convert_df(results_df)
st.download_button(label="Download data as CSV", data=csv, file_name='Classified_Image2.csv', mime='text/csv',)

